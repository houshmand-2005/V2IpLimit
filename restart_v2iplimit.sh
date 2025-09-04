#!/bin/bash

# نام session screen
SCREEN_NAME="v2iplimit_screen"

# بستن تمام sessionهایی که این اسم رو دارن
screen -list | grep "$SCREEN_NAME" | awk '{print $1}' | while read -r session; do
    screen -S "${session}" -X quit
done

# اجرای مجدد برنامه در screen
screen -dmS "$SCREEN_NAME" python3.11 /root/V2IpLimit/v2iplimit.py
