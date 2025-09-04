import requests
import os

# Telegram Bot Information
BOT_TOKEN = ""
ADMIN_ID = ""

# File paths
LOG_FILE_PATH = "/root/V2IpLimit/connections_log.txt"
COUNTER_FILE_PATH = "/root/V2IpLimit/counter.txt"

# Function to read the counter from file
def read_counter():
    if not os.path.exists(COUNTER_FILE_PATH):
        return 0  # If file doesn't exist, start from 0
    with open(COUNTER_FILE_PATH, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0  # If file is corrupted, reset to 0

# Function to update the counter
def update_counter(value):
    with open(COUNTER_FILE_PATH, "w") as f:
        f.write(str(value))

# Function to send the log file to Telegram
def send_log_file():
    if not os.path.exists(LOG_FILE_PATH):  # Check if file exists
        send_message("?? Log file not found!")
        return

    if os.path.getsize(LOG_FILE_PATH) == 0:  # Check if file is empty
        send_message("?? Log file is empty.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(LOG_FILE_PATH, "rb") as f:
        files = {"document": f}
        data = {"chat_id": ADMIN_ID, "caption": "? Log file sent successfully"}
        response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        counter = read_counter() + 1  # Increase counter
        if counter >= 24:
            open(LOG_FILE_PATH, "w").close()  # Clear log file
            update_counter(0)  # Reset counter
            send_message("??? Log file cleared after 24 uploads!")
        else:
            update_counter(counter)  # Save new counter value

# Function to send a text message to Telegram
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=data)

# Run once and exit
if __name__ == "__main__":
    send_log_file()
