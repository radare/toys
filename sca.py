#!/usr/bin/python
#
# Scapy-based application level sniffer
#
# author: pancake <youterm.com>
#

import sys
import re
import os
import array
from binascii import *
from re import *
from string import *
from scapy import *


#PcapFilename='bakala.pcap'
Iface='ath0'
PcapFilename='roflcode.pcap'
bpfilter='port 4000'

# TODO .show timestamp and packet number
# TODO : log into different files (per type based)
# TODO httpfilter='html'
bpfilter=''
dport = 4000
verbose = 0

counter = 0

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def dump2(src, length=8):
    result=[]
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       printable = s.translate(FILTER)
       result.append("%04X   %-*s   %s\n" % (i, length*3, hexa, printable))
    return ''.join(result)

ips = list();
ports = list();

def is_lan(ip):
	rexp = re.compile("^(192\.168|10\.0|172\.26)")
	if rexp.match(ip):
		return True
	return False

def add_ip(ip):
	for i in ips:
		if ip == i:
			return
	# not found
	if is_lan(ip):
		print "LAN %s"%ip
	else:
		print "INET %s"%ip

	# TODO: resolve IP
	#os.system("printf 'HOSTNAME ' && host %s"%ip)
	ips.append(ip)

def add_port(port):
	for i in ports:
		if port == i:
			return
	# not found
	print "DPORT %d"%port
	os.system("printf 'SERVICE ' && grep -e '\t%d/' /etc/services | head -n 1"%port)
	ports.append(port)

# if "fo" in "foo":
def handle_google_search(str):
	google = re.compile("\/search\?")   # google
	av     = re.compile("web\/results\?")  # altavista
	if (google.search(str) or av.search(str)):
		s = str.split('q=')[1]
		s = s.split('&')[0]
		s = s.replace('+',' ')
		print "SEARCH %s"%s

def handle_smtp(str):
	rexp = re.compile("^(USER|PASS|user|pass)")
	if rexp.match(str):
		print str

def print_package(p):
	str = p['Raw.load']

	add_ip(p['IP'].src)
	add_ip(p['IP'].dst)
	#add_port(p['TCP'].sport)
	if not is_lan(p['IP'].dst):
		add_port(p['TCP'].dport)

	if verbose:
		if dport == p['TCP'].dport:
			print("%c[0m"%0x1b)
		else:
			print("%c[32m"%0x1b)
		print("[%d] %s -> %s"%(counter, p['IP'].src, p['IP'].dst))
		print("[%d] %d -> %d"%(counter, p['TCP'].sport,p['TCP'].dport))

	if str[:3] == 'GET' or str[:4] == 'POST' or str[:4] == 'HEAD':
		lines = str.split("\n")
		method = lines[0].split(" ")[0]
		uri = lines[0].split(" ")[1]
		cookie = ''
		host = ''
		length = 0
		for line in lines:
			rexp = re.compile('^Host: ')
			#if verbose:
			#print line
			if rexp.match(line):
				host = line.split(":")[1][1:][:-1]
		for line in lines:
			rexp = re.compile('^Cookie: ')
			if rexp.match(line):
				cookie = line.split(":")[1][1:][:-1]
				print "COOKIE %s"%cookie

		content = ''
		length = 0
		next = False
		for line in lines:
			line = line[:-1]
			rexp = re.compile('^Content-Length: ')
			
			#print "LINE(%s)"%line
			if line == '':
				next=True
				continue
			if next:
				content = line
				next = False
				continue
			if rexp.match(line):
				length = line.split(":")[1][1:]

		print ("HTTP %s http://%s/%s"%(method, host, uri)).replace("//","/")
		if content != '':
			print "CONTENT (%s) %s"%(length,content)
		handle_google_search(uri)
	else:
		if verbose:
			print dump2(p['Raw.load'], 16)
			print("%c[0m"%0x1b)

def processpacket(p):
        global counter
        global dport
        counter = counter + 1
        if type(p[TCP]) == TCP and type(p[IP]) == IP and p['IP'].proto == 6:
                payload = p['Raw.load']
                if (payload != None):
			print_package(p)
	sys.stdout.flush()
# main loop

if Iface != "":
	sniff (
		store   = 0,
		iface   = Iface,
		filter  = bpfilter,
		promisc = True,
		prn     = lambda x: processpacket(x)
	)
else:
	sniff (
		store   = 0,
		offline = PcapFilename,
		filter  = bpfilter,
		prn     = lambda x: processpacket(x)
	)
