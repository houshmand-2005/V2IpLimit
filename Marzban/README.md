# V2IpLimit

Limiting the number of active users with IP
<br>[**Marzban version**](https://github.com/Gozargah/Marzban)
<br>
It also supports Marzban-node<br>

At first you need add this to your xray config file :

```bash
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

Then you need to enter your domain or server IP in the v2iplimit config.json file

To run this program

```bash
git clone https://github.com/houshmand-2005/V2IpLimit.git
cd V2IpLimit
cd Marzban
python3 v2_ip_limit.py
```

You can change [this file](v2iplimit_config.json) according to your needs:

```bash
{
  "WRITE_LOGS_TF": "True", // --> write the logs like who disable and how many users are active now and ...
  "SEND_LOGS_TO_TEL": "False", // --> send logs to a telegram bot
  "LIMIT_NUMBER": 2, // --> number of active IPs for all users
  "LOG_FILE_NAME": "ip_email.log",
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
  "SPECIAL_LIMIT": [
        ["user1", 4],
        ["user2", 1]
    ] // --> You can apply any number of IP limit per user like this, user1 can have 4 IPs
}
```

<br>
This program is activated every <b>4 minutes (you can change it)</b>, it sends information, and users who have used more than the specified number of IPs are deactivated, and after 4 minutes, all users are activated. And it is checked again if there is a need to deactivate the user in these 4 minutes, and if so, it will do so.
And again after 4 minutes all users are activated and...

<b>As a result, users who use more than the specified IP cannot use their account unless they are equal to or less than the IP limit.</b>

## Important note

As you know, this program must always be running, so there are many ways to do this, but I recommend using the screen command (be sure to read about it so you don't get into trouble.)<br>
First, hit the screen command<br>

```bash
screen
```

On the screen that opens, press the space bar Then run the program.<br>
Now you can keep the program running in the background with the combined control A and D. Now if your connection to the server is interrupted, the program will remain running.

<hr>
To see active screens 
<br>Run this command<br>

```bash
screen -ls
```

<br>And to go to that screen, this command

```bash
screen -r {id}
```

<hr>

Video tutorial:<br>

https://github.com/houshmand-2005/V2IpLimit/assets/77535700/7881347e-8b14-4569-a3b0-bc7e5703be39

If this program was useful for you, please give it a star ⭐
