import speedtest

def get_speedtest_results():
    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=None)
    s.results.share()
    print(s.results.dict())
    pass

def main():
    thread = threading.Thread(target=get_speedtest_results)
    thread.start()
    pass