#!/usr/bin/env bash

# Start resin-wifi-connect
export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

./wifi-connect -a 600