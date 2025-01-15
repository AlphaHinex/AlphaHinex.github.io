#!/bin/bash

# Check if the network cable is connected (en8 is depended)
#if ifconfig en8 | grep -q "status: active"; then
#    in_office_env=true
#else
#    in_office_env=false
#fi

# Check if outer display is connected
if system_profiler SPDisplaysDataType | grep TG34C3U; then
    in_office_env=true
else
    in_office_env=false
fi

if $in_office_env; then
    # Disable Wi-Fi
    # networksetup -setairportpower en0 off
    # Open apps
    open -a "Proxifier 2"
    osascript -e 'tell application "Proxifier 2" to set visible of every window to false'
    open -a "Lark"
    # open -a "WeChat"
    # TODO Login WeChat
    open -a "印象笔记"
    open -a "Google Chrome"
    open -a "Microsoft Remote Desktop"
    # TODO Connect tsj
else
    # Enable Wi-Fi
    networksetup -setairportpower en0 on
fi
