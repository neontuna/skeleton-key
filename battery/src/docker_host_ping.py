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
    
    while True:
        print('checking status')

        eth0_packet_loss = packet_loss('eth0')
        wlan0_packet_loss = packet_loss('wlan0')
        wwan0_packet_loss = packet_loss('wwan0')
        
        if eth0_packet_loss == None or int(eth0_packet_loss.group()) > 50:
            print('eth0 offline!')
        else:
            print('eth0 online!')
        
        if wlan0_packet_loss == None or int(wlan0_packet_loss.group()) > 50:
            print('wlan0 offline!')
        else:
            print('wlan0 online!')
        
        if wwan0_packet_loss == None or int(wwan0_packet_loss.group()) > 50:
            print('wwan0 offline!')
        else:
            print('wwan0 online!')
            
        i = i + 1
        sleep(1)
    
if __name__ == '__main__':
    main()