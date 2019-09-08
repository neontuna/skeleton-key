from time import sleep
from subprocess import PIPE
import subprocess
import re
        
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
            
        i += 1
        sleep(1)
    
if __name__ == '__main__':
    main()