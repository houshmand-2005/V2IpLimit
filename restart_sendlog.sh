#!/bin/bash

# مسیر اسکریپت جدید
PROGRAM_PATH="/root/V2IpLimit/sendlog.py"
SCREEN_NAME="sendlog"

# بررسی اینکه آیا screen اجرا شده است یا نه
if screen -list | grep -q "$SCREEN_NAME"; then
    echo "برنامه در حال اجرا است. نیازی به اجرای مجدد نیست."
    exit 0
fi

# بررسی اینکه آیا پردازش در حال اجرا است یا نه
if pgrep -f "$PROGRAM_PATH" > /dev/null; then
    echo "پردازش قدیمی در حال اجرا است، توقف آن..."
    pkill -f "$PROGRAM_PATH"
    sleep 2  # تاخیر برای بستن پردازش قبلی
fi

# اجرای مجدد برنامه در screen
echo "اجرای برنامه در screen..."
screen -dmS "$SCREEN_NAME" python3 "$PROGRAM_PATH"
echo "برنامه با موفقیت راه‌اندازی شد."
