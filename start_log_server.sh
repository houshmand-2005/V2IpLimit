#!/bin/bash

# نام اسکرین
SCREEN_NAME="log_server"

# بررسی کن که آیا سرور در حال اجرا هست یا نه
if screen -list | grep -q "$SCREEN_NAME"; then
    echo "✅ برنامه در حال اجرا است. نیاز به اجرای مجدد نیست."
else
    echo "⚡ سرور لاگ اجرا شد!"
    screen -dmS "$SCREEN_NAME" uvicorn log_server:app --host 0.0.0.0 --port 2222 --reload --app-dir /root/V2IpLimit
fi
