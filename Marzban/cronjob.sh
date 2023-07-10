#!/bin/bash

echo "Script executed at $(date)" >> /root/V2IpLimit/Marzban/cron_start.log
cd /root/V2IpLimit/Marzban/

if pgrep -f /root/V2IpLimit/Marzban/v2_ip_limit.py > /dev/null; then
    pkill -f /root/V2IpLimit/Marzban/v2_ip_limit.py
    sleep 3
    python3 /root/V2IpLimit/Marzban/v2_ip_limit.py
else
    python3 /root/V2IpLimit/Marzban/v2_ip_limit.py
fi