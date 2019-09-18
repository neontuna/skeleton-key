#!/usr/bin/env python
# The previous line ensures that this script is run under the context
# of the Python interpreter. Next, import the Scapy functions:
import json
import requests
import threading
from time import sleep
from scapy.all import *

observedclients = []

def sniffmgmt(p):
    stamgmtstypes = (0, 2, 4)
    if p.haslayer(Dot11FCS):
        if p.type == 0 and p.subtype in stamgmtstypes:
            if p.addr2 not in observedclients:
                observedclients.append(p.addr2)

def get_sniffer_results():
	interface = "wextmon"
	observedclients = []

	session = AsyncSniffer(iface=interface, prn=sniffmgmt, store=False)
    print(observedclients)
	session.start()
	sleep(60)
	session.stop()
    print(observedclients)
	
	post_results()
	
def post_results():
	url = 'http://rabbu-testing.ngrok.io/webhooks/wifi_sniffer'
	data = {"clients" : observedclients}
	requests.post(url, json=data)

def main():
	thread = threading.Thread(target=get_sniffer_results)
	thread.start()