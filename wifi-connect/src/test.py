import subprocess

wifi_connect = False

try:
    wifi_connect = subprocess.check_output(["pgrep", "wii-connec"]).strip().decode('UTF-8')
    # import code; code.interact(local=dict(globals(), **locals()))
except subprocess.CalledProcessError:
    pass

print(wifi_connect)