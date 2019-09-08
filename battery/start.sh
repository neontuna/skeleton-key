#!/usr/bin/env bash

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

while [[ true ]]; do
  # dbus-send --system --print-reply \
  #           --dest=org.freedesktop.NetworkManager \
  #           /org/freedesktop/NetworkManager \
  #           org.freedesktop.DBus.Properties.Get \
  #           string:"org.freedesktop.NetworkManager" \
  #           string:"ActiveConnections"
  # sleep 10
  
  python3 src/main.py
  sleep infinity
done