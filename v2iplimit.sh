#!/bin/bash

if ! command -v screen &>/dev/null; then
    echo "The 'screen' command is not installed."
    echo "You can install it with 'sudo apt install screen' on Ubuntu/Debian, or 'sudo yum install screen' on CentOS/RHEL."
    exit 1
fi

if ! command -v wget &>/dev/null; then
    echo "The 'wget' command is not installed."
    echo "You can install it with 'sudo apt install wget' on Ubuntu/Debian, or 'sudo yum install wget' on CentOS/RHEL."
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "The 'jq' command is not installed."
    echo "You can install it with 'sudo apt install jq' on Ubuntu/Debian, or 'sudo yum install jq' on CentOS/RHEL."
    exit 1
fi

download_program() {
    local architecture=$(uname -m)
    local url
    local filename

    if [ "$architecture" == "x86_64" ]; then
        url="https://github.com/houshmand-2005/V2IpLimit/releases/download/1.0.6/v2iplimit_amd64_linux.bin"
        filename="v2iplimit_amd64.bin"
    elif [ "$architecture" == "aarch64" ]; then
        url="https://github.com/houshmand-2005/V2IpLimit/releases/download/1.0.6/v2iplimit_arm64_linux.bin"
        filename="v2iplimit_arm64.bin"
    else
        echo "Unsupported architecture: $architecture"
        return
    fi

    if [ ! -f "$filename" ]; then
        wget "$url" -O "$filename"
        chmod +x "$filename"
    fi
}

update_program() {
    local filename

    if [ "$(uname -m)" == "x86_64" ]; then
        filename="v2iplimit_amd64.bin"
    elif [ "$(uname -m)" == "aarch64" ]; then
        filename="v2iplimit_arm64.bin"
    else
        echo "Unsupported architecture: $(uname -m)"
        return
    fi

    if [ -f "$filename" ]; then
        rm "$filename"
    fi

    download_program
    echo "The program has been updated."
}
is_running() {
    screen -list | grep -q "v2iplimit"
}

start_program() {
    local filename

    if [ "$(uname -m)" == "x86_64" ]; then
        filename="v2iplimit_amd64.bin"
    elif [ "$(uname -m)" == "aarch64" ]; then
        filename="v2iplimit_arm64.bin"
    else
        echo "Unsupported architecture: $(uname -m)"
        return
    fi

    if [ ! -f "config.json" ] || [ "$(jq -r '.BOT_TOKEN' config.json)" == "null" ]; then
        echo "BOT_TOKEN is not set. Please set it before starting the program. Run the script again and choose option 5."
        return
    fi

    if [ ! -f "config.json" ] || [ "$(jq -r '.ADMINS' config.json)" == "null" ]; then
        echo "ADMINS is not set. Please set it before starting the program. Run the script again and choose option 6."
        return
    fi

    download_program

    if is_running; then
        echo "The program is already running."
    else
        screen -Sdm v2iplimit bash -c "./$filename"
        echo "The program has been started."
    fi
}

stop_program() {
    if is_running; then
        screen -S v2iplimit -X quit
        echo "The program has been stopped."
    else
        echo "The program is not running."
    fi
}

attach_program() {
    if is_running; then
        echo "You are about to attach to the program's screen session. To detach without stopping the program, press Ctrl-a followed by d."
        read -p "Do you want to continue? (y/n) " confirm
        if [[ $confirm == [Yy]* ]]; then
            screen -r v2iplimit
        else
            echo "Operation cancelled."
        fi
    else
        echo "The program is not running."
    fi
}

create_or_update_token() {
    local token
    local confirm

    if [ -f "config.json" ]; then
        token=$(jq -r '.BOT_TOKEN' config.json)
        echo "Current BOT_TOKEN is: $token"
        read -p "Do you want to change it? (y/n) " confirm
        if [[ $confirm != [Yy]* ]]; then
            return
        fi
    fi

    echo "You must create a bot and get the token, you can get it from @BotFather in Telegram."
    read -p "Enter new BOT_TOKEN: " token

    if [ -f "config.json" ]; then
        jq --arg token "$token" '.BOT_TOKEN = $token' config.json >tmp.json && mv tmp.json config.json
    else
        echo "{\"BOT_TOKEN\": \"$token\"}" >config.json
    fi

    echo "The BOT_TOKEN has been updated."
    echo "To apply the changes, you need to restart the program."
}

create_or_update_admins() {
    local admin
    local confirm

    if [ -f "config.json" ]; then
        admin=$(jq -r '.ADMINS' config.json)
        echo "Current ADMIN is: $admin"
        read -p "Do you want to change it? (y/n) " confirm
        if [[ $confirm != [Yy]* ]]; then
            return
        fi
    fi

    echo "You must set your chat ID, you can get it from @userinfobot in Telegram."
    echo "Enter the chat ID of the admin."
    read -p "Enter new ADMIN: " admin

    if [ -f "config.json" ]; then
        jq --arg admin "$admin" '.ADMINS = [$admin | tonumber]' config.json >tmp.json && mv tmp.json config.json
    else
        echo "{\"ADMINS\": [$admin]}" >config.json
    fi

    echo "The ADMIN has been updated."
}
if [ $# -eq 0 ]; then
    while true; do
        echo "-----------------------------"
        echo "1. Start the script"
        echo "2. Stop the script"
        echo "3. Attach to the script"
        echo "4. Update the script"
        echo "5. Create or Update telegram BOT_TOKEN"
        echo "6. Create or Update ADMINS"
        echo "7. Exit"
        echo "-----------------------------"
        read -p "Enter your choice: " choice

        case $choice in
        1) start_program ;;
        2) stop_program ;;
        3) attach_program ;;
        4) update_program ;;
        5) create_or_update_token ;;
        6) create_or_update_admins ;;
        7) break ;;
        *) echo "Invalid choice. Please enter 1, 2, 3,... or 7." ;;
        esac

        echo ""
    done
else
    case $1 in
    start) start_program ;;
    stop) stop_program ;;
    update) update_program ;;
    *) echo "{start|stop|update}" ;;
    esac
fi
