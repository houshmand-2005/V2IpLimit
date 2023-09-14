# V2IpLimit

Limiting the number of active users with IP
<br>[**Marzban version**](https://github.com/Gozargah/Marzban)
<br>
It also supports Marzban-node<br>

At first you need add this to your xray config file :

```json
"log": {
    "loglevel": "info"
},
```

![loglevel](https://github.com/houshmand-2005/V2IpLimit/assets/77535700/e4b72d49-e523-4f7b-b22c-dd2f1c4403a3)
**then save it**

<hr>

You must install these libraries:

```bash
sudo apt update
apt install python3-pip
pip install websockets
pip install pytz
```

Then clone the project

```bash
git clone https://github.com/houshmand-2005/V2IpLimit.git
cd V2IpLimit
cd Marzban
```

Then you need to enter your domain or server IP in the [v2iplimit_config.json](v2iplimit_config.json) file

To run the program You have 2 options :

1. [Using the screen](#screen) (recommended) with this [Video guide](#video-tutorial)
2. [Using CronJob](#cronjob)

<hr>

You can change [this file](v2iplimit_config.json) according to your needs:

```json
{
  "WRITE_LOGS_TF": "True", // --> write the logs like who disable and how many users are active now and ...
  "SEND_LOGS_TO_TEL": "False", // --> send logs to a telegram bot
  "LIMIT_NUMBER": 2, // --> number of active IPs for all users
  "LOG_FILE_NAME": "log_file_name.log",
  "TELEGRAM_BOT_URL": "https://api.telegram.org/bot[add_your_bot_token_here]/sendMessage", // --> get your token from @BotFather and delete the '[' and ']'
  "CHAT_ID": 111111111, // get from here --> @RawDataBot
  "EXCEPT_USERS": [
        "Username",
        "Username2"
  ], // --> Accounts in this list will not be deactivated
  "PANEL_USERNAME": "admin", // --> Add your Marzban username here
  "PANEL_PASSWORD": "admin", // --> Add your Marzban password here
  "PANEL_DOMAIN": "sub.domain.com:443", // --> Add your Marzban domain name with port here
  "TIME_TO_CHECK": 240, // --> Check every x seconds (240 = 4minutes)
  "INACTIVE_DURATION": 210, // --> You can specify how long users should be disabled (in seconds)
  "SPECIAL_LIMIT": [
        ["user1", 4],
        ["user2", 1]
    ], // --> You can apply any number of IP limit per user like this, user1 can have 4 IPs
  "SERVER_NAME": "", // --> Optional, You can give your script a name that will appear in your logs.
  "PRETTY_PRINT": "True" // --> Optional, Logs will be sent to you in Telegram with a better appearance
}
```

<br>
This program is activated every <b>4 minutes (you can change it with <code>TIME_TO_CHECK</code>)</b>, it sends information, and users who have used more than the specified number of IPs are deactivated, and after x minutes(According to <code>INACTIVE_DURATION</code>), all users are activated. And it is checked again if there is a need to deactivate the user in these x minutes, and if so, it will do so.
And again after x minutes all users are activated and...

<b>As a result, users who use more than the specified IP cannot use their account unless they are equal to or less than the IP limit.</b>

<hr>

## Important notes

### screen

[Video guide](#video-tutorial)<br>
As you know, this program must always be running, so there are many ways to do this, but I recommend using the screen command (be sure to read about it so you don't get into trouble.)<br>
First, hit the screen command<br>

```bash
screen
```

On the screen that opens, press the space bar Then run the program.<br>

```bash
python3 v2_ip_limit.py
```

Now you can keep the program running in the background with the combined control A and D. Now if your connection to the server is interrupted, the program will remain running.

<b>To see active screens</b> Run this command<br>

```bash
screen -ls
```

And to go to that screen, this command

```bash
screen -r {id}
```

<hr>

### CronJob

```bash
chmod +x cronjob.sh v2_ip_limit.py
```

Then open your crontab

```bash
crontab -e
```

Then add this line to your crontab<br>
`10 */6 * * * /root/V2IpLimit/Marzban/cronjob.sh >> /root/V2IpLimit/Marzban/cron_logs_run.log 2>&1`
<br>this means every 6 hours and 10 minutes, disable the program and run it again(You can change the time of this scheduling. [tutorial](https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules))

This way works if you have cloned the project in the <b>root</b>, otherwise you have to change the path of the files according to the location of the folder in the cronjob and [this file](cronjob.sh)

every time the crontab is working, it adds a logs to this file <code>crontab_log.log</code><sub>(in this path V2IpLimit/Marzban/)</sub> so with this you can make sure your scheduling is working

<hr>

### Tips on location

To change the time of the logs to your local time And considering only the IPs related to your country change line 27 and 28 of the [v2_ip_limit.py](v2_ip_limit.py) file. <sub>(By default they are Iran)</sub>

<hr>

### Video tutorial:

<br>

https://github.com/houshmand-2005/V2IpLimit/assets/77535700/7881347e-8b14-4569-a3b0-bc7e5703be39

<hr>

### Donation

If you found V2IpLimit useful and would like to support its development, you can donate on the following crypto network:

- TRON network (TRX): `TLARb1Ns5vA7pH6wqSyZGreDbGooS85Mi5`

Thank you for your support!

<hr>

If this program was useful for you, please give it a star ⭐
