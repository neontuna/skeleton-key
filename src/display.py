import subprocess
import time
import RPi.GPIO as GPIO
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

def main():
    SSID = None
    counter = 0
    global displaying 
    
    while GPIO.input(10) == 1:
        if displaying != 'reset':
            lcd.clear()
            displaying = 'reset'
        time.sleep(1)
        counter = counter + 1
        
        lcd.setCursor(0,0)
        lcd.message('Resetting')
        
        if counter == 9:
            lcd.clear()
            lcd.message('Reset')
            break
        
        if GPIO.input(10) == 0:
            counter = 0
            break
    
    try:
        SSID = subprocess.check_output(["iwgetid", "-r"]).strip().decode('UTF-8')
        # import code; code.interact(local=dict(globals(), **locals()))
    except subprocess.CalledProcessError:
        pass
        
    if SSID is None:
        if displaying != 'disconnected':
            lcd.clear()
            displaying = 'disconnected'
        lcd.setCursor(0,0)
        lcd.message('Not connected')
    else:
        if displaying != 'ssid':
            lcd.clear()
            displaying = 'ssid'
        lcd.setCursor(0,0)
        lcd.message('Connected to:\n' + SSID)
        
if __name__ == "__main__":
    main()