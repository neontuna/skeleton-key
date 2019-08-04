import time
import display
import led

def main():
    while True:
        display.main()
        
        time.sleep(5)
        
if __name__ == "__main__":
    try:
        main()
    except:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        led.destroy()
        display.destroy()