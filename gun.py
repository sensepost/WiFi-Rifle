#!/usr/bin/python
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#  lcd_16x2.py
#  16x2 LCD Test Script
#
# Author : Matt Hawkins
# Date   : 06/04/2015
#
# http://www.raspberrypi-spy.co.uk/
#
#--------------------------------------

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import RPi.GPIO as GPIO
import time

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 17
LCD_D6 = 23
LCD_D7 = 18
LCD_BUTTON = 15
LCD_BUTTON1 = 4
LCD_BUTTON2 = 24
LCD_BUTTON3 = 27
LCD_BUTTON4 = 22

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def main():
  # Main program block

  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  GPIO.setup(LCD_BUTTON,GPIO.IN)
  GPIO.setup(LCD_BUTTON1,GPIO.IN, pull_up_down = GPIO.PUD_UP)
  GPIO.setup(LCD_BUTTON2,GPIO.IN, pull_up_down = GPIO.PUD_UP)
  GPIO.setup(LCD_BUTTON3,GPIO.IN, pull_up_down = GPIO.PUD_UP)
  GPIO.setup(LCD_BUTTON4,GPIO.IN, pull_up_down = GPIO.PUD_UP)

  # add GPIO button events
  GPIO.add_event_detect(LCD_BUTTON1, GPIO.FALLING, callback=lcdFunction, bouncetime=300) 
  GPIO.add_event_detect(LCD_BUTTON2, GPIO.FALLING, callback=lcdFunction, bouncetime=300)
  GPIO.add_event_detect(LCD_BUTTON3, GPIO.FALLING, callback=lcdFunction, bouncetime=300)
  GPIO.add_event_detect(LCD_BUTTON4, GPIO.FALLING, callback=lcdFunction, bouncetime=300)

  # Initialise display
  lcd_init()
  lcd_string("Wrieless De-Auth Gun",LCD_LINE_1)
  lcd_string("PeW PeW !!",LCD_LINE_2)
  
  while True:
    pass
    # Send some test
    #lcd_string("16x2 LCD Test",LCD_LINE_2)
    #time.sleep(3) # 3 second delay

    # Send some text
    #lcd_string("Wrieless De-Auth Gun",LCD_LINE_1)
    #lcd_string("PeW PeW !!",LCD_LINE_2)
    #time.sleep(3) # 3 second delay

def lcdclear():
	lcd_string("",LCD_LINE_1)
	lcd_string("",LCD_LINE_2)	

def lcdFunction(channel):
	#print(channel)
	lcdclear()
	if channel == 4:
		lcd_string("BUTTON 1 PRESSED",LCD_LINE_1)
	elif channel == 24:
		lcd_string("BUTTON 2 PRESSED",LCD_LINE_1)
	elif channel == 27:
		lcd_string("BUTTON 3 PRESSED",LCD_LINE_1)
	elif channel == 22:
		lcd_string("BUTTON 4 PRESSED",LCD_LINE_1)
	time.sleep(3)
	lcdclear()	
		

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display




  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
