#!/bin/bash

# Check if the network cable is connected (en8 is depended)
if ifconfig en8 | grep -q "status: active"; then
    network_cable_active=true
else
    network_cable_active=false
fi

if $network_cable_active; then
    # Disable Wi-Fi
    networksetup -setairportpower en0 off
    # Open apps
    open -a "Proxifier 2"
    osascript -e 'tell application "Proxifier 2" to set visible of every window to false'
    open -a "Lark"
    open -a "WeChat"
    # TODO Login WeChat
    open -a "印象笔记"
    open -a "Google Chrome"
    open -a "Microsoft Remote Desktop"
    # TODO Connect tsj
else
    # Enable Wi-Fi
    networksetup -setairportpower en0 on
fi