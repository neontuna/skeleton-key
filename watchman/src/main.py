from time import sleep
from subprocess import PIPE
from balena import Balena
import sys, os, re, subprocess, getopt, json, requests
import NetworkManager
import probemon
import speedmon
import batterymon

balena = Balena()
balena.auth.login_with_token(os.environ['BALENA_API_KEY'])
        
def packet_loss(interface):
    try:
        cmd = "ping -w 5 -I {0} 8.8.8.8".format(interface)
        ping_results = subprocess.run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        return re.search("\d+(?=% packet loss)", ping_results.stdout.strip().decode())
    except subprocess.CalledProcessError:
        pass

def main():
    i = 0
    eth0_online = False
    wint_online = False
    ppp0_online = False
    
    while True:
        print('Checking Internet status')

        # eth0_packet_loss = packet_loss('eth0')
        wint_packet_loss = packet_loss('wint')
        ppp0_packet_loss = packet_loss('ppp0')
        
        # eth0_online = eth0_packet_loss != None and int(eth0_packet_loss.group()) < 50
        wint_online = wint_packet_loss != None and int(wint_packet_loss.group()) < 50
        ppp0_online = ppp0_packet_loss != None and int(ppp0_packet_loss.group()) < 50
        
        print("wifi: {0}, ppp0: {1}".format(wint_online, ppp0_online))
        
        if wint_online == False and ppp0_online == False and os.environ['CELLULAR_FAILOVER'] == 'enabled':
            print("Failing over to cellular backup")
            activate_connection(['cellular'])
        elif wint_online == True and ppp0_online == True:
            print("Main connection online, disabling cellular backup")
            deactivate_connection(['cellular'])
            
        if(i%300==0):
            print("Checking for wireless clients")
            probemon.main()
            
        if(i%3600==0) and wint_online == True:
            print("Running speed test")
            speedmon.main()
        
        sleep(15)
        
        get_wifi_info()
        get_cellular_info()
        batterymon.update_battery_tags()
        
        print(i)
        i += 30
        sleep(15)
        
        post_metrics_update()
        
def post_metrics_update():
    url = 'http://rabbu-testing.ngrok.io/webhooks/status'
    data = {"device_uuid" : os.environ['BALENA_DEVICE_UUID']}
    for obj in balena.models.tag.device.get_all():
        data[obj['tag_key']] = obj['value']

    requests.post(url, json=data)
    pass
        
def get_wifi_info():
    for ap in NetworkManager.AccessPoint.all():
        try:
            update_tag('wifi_ssid', ap.Ssid)
            update_tag('wifi_signal_strength', ap.Strength)
        except NetworkManager.ObjectVanished:
            pass
            
def get_cellular_info():
    cmd = subprocess.run("mmcli -m 0 --simple-status | awk '/signal quality/||/state/ {print $4}'", shell=True, stdout=PIPE, stderr=PIPE)
    output = cmd.stdout.strip().decode().replace("'", "")
    info_array = [y for y in (x.strip() for x in output.splitlines()) if y]
    update_tag('cellular_state', info_array[0])
    update_tag('cellular_signal_strength', info_array[1])
    
def update_tag(tag, variable):
    balena.models.tag.device.set(os.environ['BALENA_DEVICE_UUID'], str(tag), str(variable))
    pass
        
def activate_connection(names):
    connection_types = ['wireless','wwan','wimax']
    connections = NetworkManager.Settings.ListConnections()
    connections = dict([(x.GetSettings()['connection']['id'], x) for x in connections])

    if not NetworkManager.NetworkManager.NetworkingEnabled:
        NetworkManager.NetworkManager.Enable(True)
    for n in names:
        if n not in connections:
            print("No such connection: %s" % n, file=sys.stderr)

        print("Activating connection '%s'" % n)
        conn = connections[n]
        ctype = conn.GetSettings()['connection']['type']
        if ctype == 'vpn':
            for dev in NetworkManager.NetworkManager.GetDevices():
                if dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED and dev.Managed:
                    break
            else:
                print("No active, managed device found", file=sys.stderr)
        else:
            dtype = {
                '802-11-wireless': 'wlan',
                'gsm': 'wwan',
            }
            if dtype in connection_types:
                enable(dtype)
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
                print("No suitable and available %s device found" % ctype, file=sys.stderr)

        NetworkManager.NetworkManager.ActivateConnection(conn, dev, "/")

def deactivate_connection(names):
    active = NetworkManager.NetworkManager.ActiveConnections
    active = dict([(x.Connection.GetSettings()['connection']['id'], x) for x in active])

    for n in names:
        if n not in active:
            print("No such connection: %s" % n, file=sys.stderr)

        print("Deactivating connection '%s'" % n)
        NetworkManager.NetworkManager.DeactivateConnection(active[n])
    
if __name__ == '__main__':
    main()