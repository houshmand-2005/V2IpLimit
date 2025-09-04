#!/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

PROGRAM_PATH="/root/V2IpLimit/check_users.py"
SCREEN_NAME="check_users"

/usr/bin/screen -list | grep -q "$SCREEN_NAME"
if [ $? -eq 0 ]; then
    echo "برنامه در حال اجرا است. نیازی به اجرای مجدد نیست."
    exit 0
fi

if pgrep -f "$PROGRAM_PATH" > /dev/null; then
    echo "پردازش قدیمی در حال اجرا است، توقف آن..."
    pkill -f "$PROGRAM_PATH"
    sleep 2
fi

echo "اجرای برنامه در screen..."
/usr/bin/screen -dmS "$SCREEN_NAME" /usr/bin/python3 "$PROGRAM_PATH"
echo "برنامه با موفقیت راه‌اندازی شد."
