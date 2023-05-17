# V2IpLimit

Limiting the number of active users with IP
<br>[**Marzban version**](https://github.com/Gozargah/Marzban)
<br>With the new Marzban update, this method will be easier soon<br>

<b>if you have problem just run this python app with sudo</b>

<b>When you use Marzban, the important thing is</b>
By default, Marzban does not show X-ray logs in the log section, so you need to change the code a little (you should do this until Marzban adds the ability to see the log).

If you are using the docker version, go to the container with this command <small>(But there is a problem 😁 Because these changes are applied inside the Docker container, if this container is changed, you have to make this change in the code again)</small>

```bash
docker exec -it dockerID bash
```

Then go to the app directory and then to the xray directory, then you need to install an editor to change the Marzban codes, such as Nano, which we install in this way.

```bash
cd app/
cd xray/
apt update
apt install nano
```

And after it is installed, open this file

```bash
nano core.py
```

And a part of the file should be removed from the comment mode <br>First find the following function and then apply this change --> logger.info(output)

```bash
    def _read_process_stdout(self):
        def reader():
            while True:
                try:
                    output = self._process.stdout.readline().strip('\n')
                    if output == '' and self._process.poll() is not None:
                        break
                except AttributeError:
                    break

                # if output:
                logger.info(output) ## Uncomment this

        threading.Thread(target=reader).start()
```

like this (It should be exactly like the photo and do not apply extra space) :

<img src="https://github.com/houshmand-2005/V2IpLimit/blob/bbac3c3ee860737bf5036b6d83740c725f5fb442/Marzban/1.png" alt="Marzban" width="800">

Then save the file and exit the container

```bash
exit
```

then you need to stop and start container to apply the changes

```bash
docker stop id
docker start id
```

<b>Now we are ready to run the script</b>

You must install these libraries:

```bash
pip install docker
pip install pytz
```

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
  "LIMIT_NUMBER": 2, // --> number of active IPs for users
  "LOG_FILE_NAME": "ip_email.log",
  "TELEGRAM_BOT_URL": "https://api.telegram.org/bot[add_your_bot_token_here]/sendMessage", // --> get your token from @BotFather
  "CHAT_ID": 111111111, // get from here --> @RawDataBot
  "EXCEPT_USERS": ["Username"], // --> Accounts in this list will not be deactivated
  "CONTAINER_ID": "auto" // --> Enter the ID of the container in which V2RayGen is running or leave it to auto. Be sure to enter the full ID**
  "PANEL_USERNAME": "admin", // --> Add your Marzban username here
  "PANEL_PASSWORD": "admin", // --> Add your Marzban password here
  "PANEL_DOMAIN": "sub.domain.com:443", // --> Add your Marzban domain name with port here
  "TIME_TO_CHECK": 360, // --> Check every x seconds (360s = 6minutes)
  "SPECIAL_LIMIT": [
        ["user1", 4],
        ["user2", 1]
    ] // --> You can apply any number of IP limit per user like this, user1 can have 4 IPs
}
```

\*\* You can do this by running the following command:<br>

```bash
sudo docker inspect --format="{{.Id}}" containername
```

<br>
This program is activated every <b>6 minutes (you can change it)</b>, it sends information, and users who have used more than the specified number of IPs are deactivated, and after 6 minutes, all users are activated. And it is checked again if there is a need to deactivate the user in these 6 minutes, and if so, it will do so.
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

If this program was useful for you, please give it a star ⭐
