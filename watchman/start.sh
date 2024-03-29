#!/usr/bin/env bash

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

# give pi a few seconds to finish boot and connect to wifi
printf 'Sleeping on boot, UDEV race fix\n'
sleep 20

# check for active wifi connection
iwgetid -r

if [ $? -eq 0 ]; then
    printf 'Skipping WiFi Connect\n'
else
    printf 'Starting WiFi Connect\n'
    ./wifi-connect -a 600 -i wint
fi

# get wlan1 ready for monitor mode
airmon-ng start wext

while [[ true ]]; do
  python3 src/main.py & # start initial python instance but return and continue
  PID1=$!

  wait $PID1
  echo 'Monitor script stopped, restarting . . .'
done

sleep infinity