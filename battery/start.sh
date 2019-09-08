#!/usr/bin/env bash

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

while [[ true ]]; do
  python3 src/main.py
  sleep infinity
done
