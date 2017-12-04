#!/usr/bin/env bash
# Intructions to setup lora gw in raspberry pi 3B

## 0.

# 1. To erase and disk for Raspbian image instalation
#     http://pingbin.com/2012/07/format-raspberry-pi-sd-card-mac-osx/
#
# 2. Use 'Etch' to mount raspbian image

# 1.
# We installed Raspbian Lite (no desktop)
# 1. Change password
# 2. enable autologin in 'sudo raspi-config'
# 3. enable interfaces: SSH and Serial
# 4. The option of 'Wait for Network at Boot' it's available
# 5. Configure wifi network
#     https://geekytheory.com/tutorial-raspberry-pi-configurar-wif/
# 6. Install pip
    sudo apt-get update
    sudo apt-get install python-pip
# 7. Download 'firmware' files
    wget https://media.giphy.com/media/dzaUX7CAG0Ihi/giphy.gif
    mv giphy.gif hello.gif


#

