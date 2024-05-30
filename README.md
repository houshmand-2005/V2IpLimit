<center>

# V2IpLimit

<b>Limiting the number of active users with IP</b><sub> (with xray logs)</sub><br>
Supports both IPv4 and IPv6 And Marzban-node

</center>

<hr>

## Table of Contents

- [Installation](#installation)
- [Telegram Bot Commands](#telegram-bot-commands)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Donations](#donations)

## Installation

You can install V2IpLimit by running the following command in your terminal:

```bash
bash <(curl -sSL https://houshmand-2005.github.io/v2iplimit.sh)
```

After running the command, you will see a menu with the following options:

```
-----------------------------
1. Start the script
2. Stop the script
3. Attach to the script
4. Update the script
5. Create or Update telegram BOT_TOKEN
6. Create or Update ADMINS
7. Exit
-----------------------------
Enter your choice:
```

![Loading Gif](readme_files/1.gif)

And after that you need input your panel information and other settings:

![Loading Gif](readme_files/1.png)

After that script runs automatically and you can see the logs.

## Telegram Bot Commands

V2IpLimit can be controlled via a Telegram bot. Here are the available commands:

- `/start`: Start the bot.
- `/create_config`: Configure panel information (username, password, etc.).
- `/set_special_limit`: Set a specific IP limit for each user (e.g., test_user limit: 5 ips).
- `/show_special_limit`: Show the list of special IP limits.
- `/add_admin`: Give access to another chat ID and create a new admin for the bot.
- `/admins_list`: Show the list of active bot admins.
- `/remove_admin`: Remove an admin's access to the bot.
- `/country_code`: Set your country. Only IPs related to that country are counted (to increase accuracy).
- `/set_except_user`: Add a user to the exception list.
- `/remove_except_user`: Remove a user from the exception list.
- `/show_except_users`: Show the list of users in the exception list.
- `/set_general_limit_number`: Set the general limit number. If a user is not in the special limit list, this is their limit number.
- `/set_check_interval`: Set the check interval time.
- `/set_time_to_active_users`: Set the time to active users.
- `/backup`: Send the 'config.json' file.

## Common Issues and Solutions

1.  **Incorrect Count of Connected IPs**

    - Why does the number of detected IPs decrease after a while?
    - This problem arises when the WebSocket connection becomes corrupted during log transmission. So you can use CronJob(for now it isn't available) method

2.  **Uninstalling V2IpLimit Script**

    - How can I uninstall the V2IpLimit script?
    - Simply Stop the script and then delete the script folder.

3.  **Connections Persisting After Disabling**

    - Users remain connected even after disabling. Why?
    - This issue is related to the xray core. Connections persist until the user manually closes them. So you have to wait a little until all the connections are closed

4.  **Restarting After Changing JSON Config File**

    - Is a restart needed after modifying the JSON config file?
    - No, a restart isn't necessary. The program adapts to changes in the JSON file in short time.

5.  **Running Script on Different VPS**

    - Can I run the script on a different VPS?
    - Absolutely, the script is flexible and works seamlessly on any VPS or even on your local machine.

6.  **Tunneling and User IP Detection**

    - Tunneling returns the tunnel server IP for users. Any solutions?
    - Tunneling poses challenges. For better IP detection, consider alternative methods [Read More Here](https://github.com/houshmand-2005/V2IpLimit/issues/3)

7.  **I'm using haproxy why I don't have logs**

    - You need to add this to your haproxy config file:
      `option forwardfor`
      And then restart your haproxy service.

8.  **I'm not using tunnel or haproxy or anything else but still I don't have logs**

    - you need add this to your xray config file(If it doesn't exist) :
      ```json
      "log": {
          "loglevel": "info"
      },
      ```

    And also See this issue : [Read More Here](https://github.com/houshmand-2005/V2IpLimit/issues/32)

## Donations

If you found V2IpLimit useful and would like to support its development, you can donate on the following crypto network:

- TRON network (TRX): `TLARb1Ns5vA7pH6wqSyZGreDbGooS85Mi5`

Thank you for your support!

If this program was useful for you, please give it a star ⭐
