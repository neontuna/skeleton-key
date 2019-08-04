#!/usr/bin/env python3
########################################################################
# Filename    : ColorfulLED.py
# Description : A auto flash ColorfulLED
# Author      : freenove
# modification: 2018/08/02
########################################################################
import RPi.GPIO as GPIO
import time
import random

pins = {'pin_R':15, 'pin_G':13, 'pin_B':11}  # pins is a dict

def setup():
    global p_R,p_G,p_B
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    for i in pins:
        GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
        GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led
    p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
    p_G = GPIO.PWM(pins['pin_G'], 2000)
    p_B = GPIO.PWM(pins['pin_B'], 2000)
    p_R.start(0)      # Initial duty Cycle = 0
    p_G.start(0)
    p_B.start(0)

def setColor(r_val,g_val,b_val):   
    p_R.ChangeDutyCycle(r_val)     # Change duty cycle
    p_G.ChangeDutyCycle(g_val)
    p_B.ChangeDutyCycle(b_val)

# def loop():
#     while True :
#         # r=random.randint(0,100)#get a random in (0,100)
#         # g=random.randint(0,100)
#         # b=random.randint(0,100)
#         # r=100
#         # g=50
#         # b=100
#         # setColor(r,g,b)#set random as a duty cycle value 
#         # print ('r=%d, g=%d, b=%d ' %(r ,g, b))
#         # time.sleep(1)
#         # p_R.ChangeDutyCycle(100)     # Change duty cycle
#         # p_G.ChangeDutyCycle(100)
#         # p_B.ChangeDutyCycle(100)
#         setRed()
#         time.sleep(1)
#         setBlue()
#         time.sleep(1)
#         setGreen()
#         time.sleep(1)
#         setYellow()
#         time.sleep(1)
        
def setRed():
    setColor(50,100,100)
    
def setGreen():
    setColor(100,50,100)
    
def setBlue():
    setColor(100,100,50)
    
def setYellow():
    setColor(50,50,100)
    
def turnOff():
    setColor(100,100,100)
        
def destroy():
    p_R.stop()
    p_G.stop()
    p_B.stop()
    GPIO.cleanup()
    
# if __name__ == '__main__':     # Program start from here
#     setup()
#     try:
#         loop()
#     except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
#         destroy()