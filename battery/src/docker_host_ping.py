from time import sleep
from subprocess import PIPE
import subprocess
import re
        
def packet_loss(interface):
    try:
        cmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -q -p 22222 $DOCKER_HOST_IP 'ping -w 5 -I {0} 8.8.8.8'".format(interface)
        ping_results = subprocess.run(cmd, shell=True, stdout=PIPE)
        return re.search("\d+(?=% packet loss)", ping_results.stdout.strip().decode()) 
    except subprocess.CalledProcessError:
        pass