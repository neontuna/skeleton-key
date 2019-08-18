import subprocess
import time
import socket
import RPi.GPIO as GPIO
import led
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD

PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print ('I2C Address Error !')
        exit(1)
        
mcp.output(3,1)     # turn on LCD backlight

lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
lcd.begin(16,2)     # set number of LCD lines and columns
displaying = None

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

led.setup()

def is_connected():
    try:
        socket.create_connection(("www.google.com", 80), 5)
        return True
    except OSError:
        pass
    return False

def destroy():
    lcd.clear()

def main():
    SSID = None
    wifi_connect = False
    counter = 0
    global displaying 
    
    while GPIO.input(10) == 1:
        time.sleep(1)
        counter = counter + 1
        
        if counter == 5:
            led.setBlue()
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.message('Resetting!')
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
            lcd.clear()
            displaying = 'wifi_connect'
        led.turnOff()
        time.sleep(1)
        led.setBlue()
        lcd.setCursor(0,0)
        lcd.message('Wifi Connect\nRunning...')    
    elif SSID is None:
        if displaying != 'disconnected':
            print('set red')
            led.setRed()
            lcd.clear()
            displaying = 'disconnected'
        lcd.setCursor(0,0)
        lcd.message('Not connected')
    elif is_connected() is False:
        if displaying != 'no_internet':
            led.setYellow()
            lcd.clear()
            displaying = 'no_internet'
        led.turnOff()
        time.sleep(1)
        led.setYellow()
        lcd.setCursor(0,0)
        lcd.message('Wireless Connected\nbut no Internet?')
    else:
        if displaying != 'ssid':
            led.setGreen()
            lcd.clear()
            displaying = 'ssid'
        lcd.setCursor(0,0)
        lcd.message('Connected to:\n' + SSID)
        
if __name__ == "__main__":
    main()