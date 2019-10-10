#!/usr/bin/env python
# The previous line ensures that this script is run under the context
# of the Python interpreter. Next, import the Scapy functions:
import json
import requests
import threading
import os
from time import sleep
from scapy.all import *
from balena import Balena

observedclients = []

balena = Balena()
balena.auth.login_with_token(os.environ['BALENA_API_KEY'])

def sniffmgmt(p):
    stamgmtstypes = (4)
    if p.haslayer(Dot11):
        if p.type == 0 and p.subtype in stamgmtstypes:
            if p.addr2 not in observedclients:
                observedclients.append(p.addr2)

def get_sniffer_results():
	interface = "wextmon"
	observedclients = []

	session = AsyncSniffer(iface=interface, prn=sniffmgmt, store=False)
	session.start()
	sleep(60)
	session.stop()
	
	post_results()
	
def post_results():
	# url = 'http://rabbu-testing.ngrok.io/webhooks/wifi_sniffer'
	# data = {"clients" : observedclients}
	# requests.post(url, json=data)
    print(observedclients)
    update_tag('wifi_client_count', len(observedclients))
    
def update_tag(tag, variable):
    # update device tags
    balena.models.tag.device.set(os.environ['BALENA_DEVICE_UUID'], str(tag), str(variable))

def main():
	thread = threading.Thread(target=get_sniffer_results)
	thread.start()