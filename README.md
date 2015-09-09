# WiFi-Rifle
By Domainic White (singe) & Saif El-Sherei @ SensePost (research@sensepost.com)

# Overview
Creating a wireless rifle de-authentication gun, which utilized a yagi antenna and a Raspberry Pi. The idea was simple: simulate some of the tools available in aircrack-ng wireless hacking suite in one script but without utilizing aircrack-ng in the process.

# Contents

It contatins:
<ul>
<li>wifi.py - Main Wifi-Deauth script.</li>
<li>gun.py - Simple Raspberry Pi Python Script to control an LED and GPIO buttons</li></ul>

<h1>Pre-Requisites </h1>
<ul>
<li>Impacket - Impacket is a collection of Python classes for working with network protocols (https://github.com/CoreSecurity/impacket).</li>
<li>Pcapy - Pcapy is a Python extension module that enables software written in Python to access the routines from the pcap packet capture library (https://github.com/CoreSecurity/pcapy).</li>
<li>Urwid  - Urwid is a console user interface library for Python (http://urwid.org/).</li>
</ul>

<h1>Running</h1>
Just supply the wireless interface to the main wifi.py script.

<pre><code>wifi.py wlan0</code></pre>

The script features:
<ol>
<li>Utilize iw commands to place a wireless device into monitor mode, and perform channel hopping to obtain packets from all channels.</li>
<li>Use Core Security’s <a href="http://www.coresecurity.com/corelabs-research/open-source-tools/pcapy">Pcapy</a> to sniff traffic of the monitor device.</li>
<li>use Core Security’s <a href="https://github.com/CoreSecurity/impacket">Impacket</a> inside threads to parse certain 802.11 packets and extract interesting data from them.</li>
<li>A <a href="http://urwid.org/">Urwid</a> a ncurses wrapper module  to display the interface and handle key presses and callbacks.</li>
<li>Use impacket to generate wireless packets and send them through raw sockets.</li>
</ol>

<h1>License</h1>
WiFi-Rifle by SensePost is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License (http://creativecommons.org/licenses/by-sa/4.0/) Permissions beyond the scope of this license may be available at http://sensepost.com/contact us/.
</br >Impacket is provided under a slightly modified version of the Apache Software License. See (https://github.com/CoreSecurity/impacket/blob/master/LICENSE) for more details.
</br >Pcapy is provided under a slightly modified version of the Apache Software License. (https://github.com/CoreSecurity/pcapy/blob/master/LICENSE) for more details.
</br >Urwid is provided under GPL v2 license. See (https://github.com/wardi/urwid/blob/master/COPYING) for more details.




