import subprocess
import time
import socket
import RPi.GPIO as GPIO
import led

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

led.setup()
displaying = None

def is_connected():
    try:
        socket.create_connection(("www.google.com", 80), 5)
        return True
    except OSError:
        pass
    return False

def main():
    wifi_connect = False
    counter = 0
    global displaying 
    
    while GPIO.input(10) == 1:
        time.sleep(1)
        counter = counter + 1
        
        if counter == 5:
            led.setBlue()
            time.sleep(1)
            subprocess.Popen(["./reset.sh"], shell=True, executable="/bin/bash")
        
        if GPIO.input(10) == 0:
            counter = 0

    try:
        SSID = subprocess.check_output(["iwgetid", "-r"]).strip().decode('UTF-8')
        # import code; code.interact(local=dict(globals(), **locals()))
    except subprocess.CalledProcessError:
        pass
        
    try:
        wifi_connect = subprocess.check_output(["pgrep", "wifi-connect"]).strip().decode('UTF-8')
        # import code; code.interact(local=dict(globals(), **locals()))
    except subprocess.CalledProcessError:
        pass

    if wifi_connect != False:
        if displaying != 'wifi_connect':
            led.setBlue()
            displaying = 'wifi_connect'
        led.turnOff()
        time.sleep(1)
        led.setBlue()
    elif SSID is None:
        if displaying != 'disconnected':
            print('set red')
            led.setRed()
            displaying = 'disconnected'
    elif is_connected() is False:
        if displaying != 'no_internet':
            led.setYellow()
            displaying = 'no_internet'
        led.turnOff()
        time.sleep(1)
        led.setYellow()
    else:
        if displaying != 'ssid':
            led.setGreen()
            displaying = 'ssid'
        
if __name__ == "__main__":
    main()