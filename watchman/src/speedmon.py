import speedtest
import sys, getopt, os
from balena import Balena

balena = Balena()
balena.auth.login_with_token(os.environ['BALENA_API_KEY'])

def update_tag(tag, variable):
    balena.models.tag.device.set(os.environ['BALENA_DEVICE_UUID'], str(tag), str(variable))

def get_speedtest_results():
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download(threads=None)
    print(s.results.dict())
    update_tag('download_speed', s.results.download_speed)
    update_tag('ping', s.results.ping)
    pass

def main():
    thread = threading.Thread(target=get_speedtest_results)
    thread.start()
    pass