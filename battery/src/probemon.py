#!/usr/bin/env python
# The previous line ensures that this script is run under the context
# of the Python interpreter. Next, import the Scapy functions:
import json
import requests
import asyncio
from time import sleep
from scapy.all import *

observedclients = []

def sniffmgmt(p):
    stamgmtstypes = (0, 2, 4)
    if p.haslayer(Dot11FCS):
        if p.type == 0 and p.subtype in stamgmtstypes:
            if p.addr2 not in observedclients:
                print(p.addr2)
                observedclients.append(p.addr2)

@async_to_sync
async def get_sniffer_results():
	interface = "wlan1mon"
	observedclients = []

	session = AsyncSniffer(iface=interface, prn=sniffmgmt, store=False)
	session.start()
	await asyncio.sleep(60)
	session.stop()
	
	post_results()
	
def post_results():
	url = 'http://34df0a2c.ngrok.io/webhooks/wifi_sniffer'
	data = {"clients" : observedclients}
	requests.post(url, json=data)

def main():
	get_sniffer_results()