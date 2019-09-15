from time import sleep
from subprocess import PIPE
import sys, os, re, subprocess
import NetworkManager
# import probemon
        
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
    wlan0_online = False
    wwan0_online = False
    
    while True:
        print('Checking Internet status')

        # eth0_packet_loss = packet_loss('eth0')
        wlan0_packet_loss = packet_loss('wlan0')
        wwan0_packet_loss = packet_loss('wwan0')
        
        # eth0_online = eth0_packet_loss != None and int(eth0_packet_loss.group()) < 50
        wlan0_online = wlan0_packet_loss != None and int(wlan0_packet_loss.group()) < 50
        wwan0_online = wwan0_packet_loss != None and int(wwan0_packet_loss.group()) < 50
        
        print("wlan0: {0}, wwan0: {1}".format(wlan0_online, wwan0_online))
        
        if wlan0_online == False and wwan0_online == False and os.environ['CELLULAR_FAILOVER'] == 'enabled':
            print("Failing over to cellular backup")
            activate_connection(['cellular'])
        elif wlan0_online == True and wwan0_online == True:
            print("Main connection online, disabling cellular backup")
            deactivate_connection(['cellular'])
            
        # if(i%300==0):
        #     print("Checking for wireless clients")
        #     probemon.main()
        
        print(i)
        i += 30
        sleep(30)
        
def get_wifi_info():
    stats = []
    for ap in NetworkManager.AccessPoint.all():
        try:
            stats = [ap.Ssid, ap.Strength]
        except NetworkManager.ObjectVanished:
            pass
    return stats
            
def get_cellular_info():
    cmd = subprocess.run("mmcli -m 0 --simple-status | awk '/signal quality/||/state/ {print $4}'", shell=True, stdout=PIPE, stderr=PIPE)
    output = cmd.stdout.strip().decode().replace("'", "")
    return [y for y in (x.strip() for x in output.splitlines()) if y]
        
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