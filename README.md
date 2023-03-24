# V2IpLimit

Limiting the number of active users with IP
<br>Currently only tested with [V2RayGen](https://github.com/SonyaCore/V2RayGen)

<b>if you have problem just run this python app with sudo</b>

<b>When you use V2RayGen, the important thing is to use this tag at the end when creating the configuration --loglevel warning </b>
<br>like this:

```bash
curl https://raw.githubusercontent.com/SonyaCore/V2RayGen/main/V2RayGen.py | sudo python3 - --vmess --loglevel warning
```

You must install this library:

```bash
pip install docker
```

You can change [this file](v2iplimit_config.json) according to your needs:

```bash
{
  "WRITE_LOGS_TF": "True", // ----> write the logs like who disable and how many users are active now and ...
  "SEND_LOGS_TO_TEL": "False", // ----> send logs to a telegram bot
  "LIMIT_NUMBER": 2, // ----> number of active IPs for users
  "EN_DIS_USERS": "en_dis_users.json",
  "LOG_FILE_NAME": "ip_email.log",
  "CONFIG_FILE": "config.json", // you must have this file
  "TELEGRAM_BOT_URL": "https://api.telegram.org/bot[add_your_bot_token_here]/sendMessage", // ----> get your token from @BotFather
  "CHAT_ID": 111111111, // get from here ----> @RawDataBot
  "EXCEPT_EMAIL": ["client@example.com"], // ----> Accounts in this list will not be deactivated
  "CONTAINER_ID": "auto" // Enter the ID of the container in which V2RayGen is running or leave it to auto. Be sure to enter the full ID**
}
```

\*\* You can do this by running the following command:<br>

```bash
sudo docker inspect --format="{{.Id}}" containername
```

<br>
This program is activated every <b>6 minutes</b>, it sends information, and users who have used more than the specified number of IPs are deactivated, and these users are written in a json file (EN_DIS_USERS) and after 6 minutes, all users are activated. And it is checked again if there is a need to deactivate the user in these 6 minutes, and if so, it will do so.
And again after 6 minutes all users are activated and...

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

If this program was useful for you, please give a star ⭐
