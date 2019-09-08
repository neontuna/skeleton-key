from time import sleep
from subprocess import PIPE
import subprocess
import re
import NetworkManager
import sys
        
def packet_loss(interface):
    try:
        cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -q -p 22222 $DOCKER_HOST_IP 'ping -w 5 -I {0} 8.8.8.8'".format(interface)
        ping_results = subprocess.run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        return re.search("\d+(?=% packet loss)", ping_results.stdout.strip().decode())
    except subprocess.CalledProcessError:
        pass

def main():
    i = 0
    eth0_online = False
    wlan0_online = False
    wwan0_online = False
    
    while True:
        print('checking status')

        eth0_packet_loss = packet_loss('eth0')
        wlan0_packet_loss = packet_loss('wlan0')
        wwan0_packet_loss = packet_loss('wwan0')
        
        eth0_online = eth0_packet_loss != None and int(eth0_packet_loss.group()) < 50
        wlan0_online = wlan0_packet_loss != None and int(wlan0_packet_loss.group()) < 50
        wwan0_online = wwan0_packet_loss != None and int(wwan0_packet_loss.group()) < 50
        
        print("eth0: {0}, wlan0: {1}, wwan0: {2}".format(eth0_online, wlan0_online, wwan0_online))
        print("...")
        
        if eth0_online == False and wlan0_online == False and wwan0_online == False:
            print("Failing over to cellular backup")
            activate_connection('cellular')
        elif wwan0_online == True and eth0_online == True or wlan0_online == True:
            print("Main connection online, disabling cellular backup")
            deactivate_connection('cellular')
            
        i += 1
        sleep(30)
        
def activate_connection(name):
    connections = NetworkManager.Settings.ListConnections()
    connections = dict([(x.GetSettings()['connection']['id'], x) for x in connections])
    conn = connections[name]

    # Find a suitable device
    ctype = conn.GetSettings()['connection']['type']
    if ctype == 'vpn':
        for dev in NetworkManager.NetworkManager.GetDevices():
            if dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED and dev.Managed:
                break
        else:
            print("No active, managed device found")
            sys.exit(1)
    else:
        dtype = {
            '802-11-wireless': NetworkManager.NM_DEVICE_TYPE_WIFI,
            '802-3-ethernet': NetworkManager.NM_DEVICE_TYPE_ETHERNET,
            'gsm': NetworkManager.NM_DEVICE_TYPE_MODEM,
        }.get(ctype,ctype)
        devices = NetworkManager.NetworkManager.GetDevices()

        for dev in devices:
            if dev.DeviceType == dtype and dev.State == NetworkManager.NM_DEVICE_STATE_DISCONNECTED:
                break
        else:
            print("No suitable and available %s device found" % ctype)
            sys.exit(1)

    # And connect
    NetworkManager.NetworkManager.ActivateConnection(conn, dev, "/")
    
def deactivate_connection(name):
    connections = NetworkManager.Settings.ListConnections()
    connections = dict([(x.GetSettings()['connection']['id'], x) for x in connections])
    conn = connections[name]

    # Find a suitable device
    ctype = conn.GetSettings()['connection']['type']
    if ctype == 'vpn':
        for dev in NetworkManager.NetworkManager.GetDevices():
            if dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED and dev.Managed:
                break
        else:
            print("No active, managed device found")
            sys.exit(1)
    else:
        dtype = {
            '802-11-wireless': NetworkManager.NM_DEVICE_TYPE_WIFI,
            '802-3-ethernet': NetworkManager.NM_DEVICE_TYPE_ETHERNET,
            'gsm': NetworkManager.NM_DEVICE_TYPE_MODEM,
        }.get(ctype,ctype)
        devices = NetworkManager.NetworkManager.GetDevices()

        for dev in devices:
            if dev.DeviceType == dtype and dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED:
                break
        else:
            print("No suitable and available %s device found" % ctype)
            sys.exit(1)

    # And disconnect
    NetworkManager.NetworkManager.DeactivateConnection(dev, "/")
    
if __name__ == '__main__':
    main()