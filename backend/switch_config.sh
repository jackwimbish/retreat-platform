#!/bin/bash

# Script to switch between local and Docker configurations

CONFIG_DIR="instance/etc"

case "$1" in
    "local")
        echo "Switching to local configuration..."
        if [ -f "$CONFIG_DIR/zope.conf.local" ]; then
            cp "$CONFIG_DIR/zope.conf.local" "$CONFIG_DIR/zope.conf"
        fi
        if [ -f "$CONFIG_DIR/zope.ini.local" ]; then
            cp "$CONFIG_DIR/zope.ini.local" "$CONFIG_DIR/zope.ini"
        fi
        echo "✓ Switched to local configuration"
        ;;
    "docker")
        echo "Switching to Docker configuration..."
        if [ -f "$CONFIG_DIR/zope.conf.docker" ]; then
            cp "$CONFIG_DIR/zope.conf.docker" "$CONFIG_DIR/zope.conf"
        fi
        if [ -f "$CONFIG_DIR/zope.ini.docker" ]; then
            cp "$CONFIG_DIR/zope.ini.docker" "$CONFIG_DIR/zope.ini"
        fi
        echo "✓ Switched to Docker configuration"
        ;;
    *)
        echo "Usage: $0 {local|docker}"
        echo "  local  - Use local development configuration"
        echo "  docker - Use Docker configuration"
        exit 1
        ;;
esac