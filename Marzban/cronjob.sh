#!/bin/bash

echo "Script executed at $(date)" >>/root/V2IpLimit/Marzban/cronjob_log.log
cd /root/V2IpLimit/Marzban/

# Terminate existing instances of v2_ip_limit.py
echo "Terminating existing instances of v2_ip_limit.py" >>cronjob_log.log
pids=$(pgrep -f v2_ip_limit.py)
if [ -n "$pids" ]; then
    echo "Existing process IDs: $pids" >>cronjob_log.log
    for pid in $pids; do
        echo "Killing process $pid" >>cronjob_log.log
        kill -9 "$pid"
    done
    sleep 5
    pids=$(pgrep -f v2_ip_limit.py)
    echo "Remaining process IDs: $pids" >>cronjob_log.log
fi

# Start v2_ip_limit.py
echo "Starting v2_ip_limit.py" >>cronjob_log.log
python3 v2_ip_limit.py
