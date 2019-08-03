#!/bin/bash

# Enable i2c - needed for the Display-O-Tron HAT
modprobe i2c-dev

# Run one process loop
python3 src/display.py

# Start resin-wifi-connect
export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

iwgetid -r

if [ $? -eq 0 ]; then
    printf 'Skipping WiFi Connect\n'
else
    printf 'Starting WiFi Connect\n'
    ./wifi-connect
fi

# At this point the WiFi connection has been configured and the device has
# internet - unless the configured WiFi connection is no longer available.

# Start the main application
python3 src/main.py