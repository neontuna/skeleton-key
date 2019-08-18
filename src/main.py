import time
import status_loop
import led

def main():
    while True:
        status_loop.main()
        
        time.sleep(5)
        
if __name__ == "__main__":
    try:
        main()
    except:
        led.destroy()