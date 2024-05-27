"""
This is very hard to test since
it requires a running panel server and a running node server
I have to test it manually
"""

import argparse
import asyncio

from run_telegram import run_telegram_bot
from utils.check_usage import ACTIVE_USERS, check_ip_used, run_check_users_usage
from utils.get_logs import (
    TASKS,
    check_and_add_new_nodes,
    create_node_task,
    create_panel_task,
    handle_cancel,
    handle_cancel_one,
)
from utils.handel_dis_users import DisabledUsers
from utils.panel_api import (
    all_user,
    disable_user,
    enable_all_user,
    enable_dis_user,
    enable_selected_users,
    get_nodes,
    get_token,
)
from utils.parse_logs import INVALID_EMAILS, check_ip, parse_logs
from utils.read_config import read_config
from utils.types import PanelType, UserType

parser = argparse.ArgumentParser(description="Help message")
parser.add_argument("--version", action="version", version="1.0.0")
args = parser.parse_args()

panel_data = PanelType("admin", "admin", "192.168.1.37:8000")
users = [
    UserType(name="Test2"),
    UserType(name="Test"),
]
INVALID_EMAILS.append("Irancell")
dis_obj = DisabledUsers()

LOGS = """
2023/07/07 03:08:59 [2a01:5ec0:5011:9962:d8ed:c723:c32:ac2a]:62316 accepted tcp:2.56.98.255:8000 [GRPC 6 >> DIRECT] email: 6.TEST_user+canyoudetec-t=me
2023/07/07 03:08:59 [Info] [2459191711] proxy/freedom: connection opened to tcp:2.56.98.255:8000, local endpoint 2.56.98.255:53768, remote endpoint 2.56.98.255:8000
2023/07/07 03:09:00 [Info] [2615434286] proxy/vless/inbound: firstLen = 0
2023/07/07 03:09:00 [Info] [2615434286] app/proxyman/inbound: connection ends > proxy/vless/encoding: failed to read request version > EOF
2023/07/07 03:09:00 [Info] [2083986186] proxy/vless/inbound: firstLen = 0
2023/07/07 03:09:00 [Info] [3858357221] proxy/vless/inbound: firstLen = 1186
2023/07/07 03:09:00 [Info] [3858357221] proxy/vless/inbound: received request for tcp:gateway.instagram.com:443
2023/07/07 03:09:00 [Info] [3858357221] proxy/vless/encoding: XtlsFilterTls found tls client hello! 234
2023/07/07 03:09:00 [Info] [3858357221] app/dispatcher: sniffed domain: gateway.instagram.com
2023/07/07 03:09:00 [Info] [3858357221] app/dispatcher: taking detour [IPv4] for [tcp:gateway.instagram.com:443]
2023/07/07 03:09:00 151.232.190.86:57288 accepted tcp:gateway.instagram.com:443 [REALITY TCP 4 -> IPv4] email: 22.User_22
2023/07/07 03:09:00 [Info] [3858357221] proxy/freedom: dialing to tcp:157.240.0.1:443
2023/07/07 03:09:00 [Info] [3858357221] transport/internet/tcp: dialing TCP to tcp:157.240.0.1:443
2023/07/07 03:09:00 [Info] [3858357221] proxy/freedom: connection opened to tcp:gateway.instagram.com:443, local endpoint 2.56.98.255:32906, remote endpoint 157.240.0.1:443
2023/07/07 03:09:00 [Info] [3858357221] proxy/vless/encoding: XtlsPadding 3222 32 0
2023/07/07 03:09:01 [Info] [2387213153] proxy/vless/inbound: firstLen = 0
2023/07/07 03:09:01 [Info] [2387213153] app/proxyman/inbound: connection ends > proxy/vless/encoding: failed to read request version > EOF
2023/07/07 03:09:01 [Info] [404727011] proxy/vless/inbound: firstLen = 0
2023/07/07 03:09:01 [Info] [404727011] app/proxyman/inbound: connection ends > proxy/vless/encoding: failed to read request version > EOF
2023/07/07 03:09:05 [Info] [2448877047] app/proxyman/inbound: connection ends > proxy/vless/encoding: failed to read request version > EOF
2023/07/07 03:09:11 [Info] [699990659] proxy/vless/encoding: XtlsFilterTls stop filtering39
2023/07/07 03:09:15 [Info] [1598447880] proxy/vless/inbound: firstLen = 260
2023/07/07 03:09:15 [Info] [1598447880] proxy/vless/inbound: received request for tcp:checkappexec.microsoft.com:443
2023/07/07 03:09:15 [Info] [1598447880] app/dispatcher: sniffed domain: checkappexec.microsoft.com
2023/07/07 03:09:15 [Info] [1598447880] transport/internet/tcp: dialing TCP to tcp:checkappexec.microsoft.com:443
2023/07/07 03:09:15 [2a01:5ec0:5011:9962:d8ed:c723:c32:ac2a]:62316 accepted tcp:checkappexec.microsoft.com:443 [GRPC 6 >> DIRECT] email: 6.TEST_user+canyoudetec-t=me  
2023/07/07 03:09:15 [Info] [1598447880] proxy/freedom: connection opened to tcp:checkappexec.microsoft.com:443, local endpoint 2.56.98.255:52964, remote endpoint 20.31.42.83:443
2023/07/07 03:09:16 [Info] [3542877761] app/proxyman/inbound: connection ends > proxy/vless/inbound: connection ends > context canceled
2023/07/07 03:09:16 [Info] [1598447880] app/proxyman/inbound: connection ends > proxy/vless/inbound: connection ends > context canceled
2023/07/07 03:09:18 [Info] [4283018094] proxy/vless/inbound: firstLen = 70
2023/07/07 03:09:18 [Info] [4283018094] proxy/vless/inbound: received request for udp:1.1.1.1:53
2023/07/07 03:09:18 [Warning] [4283018094] app/dispatcher: non existing outTag: DNS-Internal
2023/07/07 03:09:18 [Info] [4283018094] proxy/freedom: connection opened to udp:1.1.1.1:53, local endpoint [::]:54582, remote endpoint 1.1.1.1:53
2023/07/07 03:09:18 [2a01:5ec0:5013:4ca8:1:0:d554:7f0e]:45572 accepted udp:1.1.1.1:53 [REALITY TCP 6 >> DIRECT] email: 2.Irancell
2023/07/07 03:09:21 [Info] transport/internet/tcp: REALITY: processed invalid connection
"""


async def add_fake_users():
    """Add some fake users to test"""
    ACTIVE_USERS.setdefault("user_name", UserType(name="user_name", ip=["9.9.9.9"]))
    ACTIVE_USERS["user_name"].ip.append("8.8.8.8")
    ACTIVE_USERS["user_name"].ip.append("8.8.8.8")
    ACTIVE_USERS["user_name"].ip.append("8.8.8.8")
    ACTIVE_USERS["user_name"].ip.append("1.1.1.1")
    ACTIVE_USERS["user_name"].ip.append("1.1.1.1")
    ACTIVE_USERS["user_name"].ip.append("1.1.1.1")
    ACTIVE_USERS.setdefault(
        "another_user",
        UserType(name="another_user", ip=["1.1.1.2"]),
    )
    ACTIVE_USERS["another_user"].ip.append("1.1.1.2")
    ACTIVE_USERS["another_user"].ip.append("1.1.1.2")
    ACTIVE_USERS["another_user"].ip.append("1.1.1.2")
    ACTIVE_USERS.setdefault("test", UserType(name="test", ip=["..."]))


async def main():  # pylint: disable=too-many-statements
    """Main function to run the code."""
    await read_config()
    asyncio.create_task(run_telegram_bot())
    await asyncio.sleep(5)
    print("Telegram Bot running...")
    await add_fake_users()
    print("Print All Active Users Before 'check_ip_used' Test: ", ACTIVE_USERS)
    await check_ip_used()
    print("Print All Active Users After 'check_ip_used' Test: ", ACTIVE_USERS)
    print("Parser Test: ", await parse_logs(LOGS))
    print("Check Ip Test: ", await check_ip("2a01:5ec0:5011:9962:d8ed:c723:c32:ac2a"))
    try:
        print("Get Token Test: ", await get_token(panel_data))
    except ValueError as error:
        print(error)
        return
    dis_users = await dis_obj.read_and_clear_users()
    print("Data in '.disable_users.json' file Test:", dis_users)
    await enable_selected_users(panel_data, dis_users)
    try:
        print("Get All Users Test: ", await all_user(panel_data))
    except Exception as error:  # pylint: disable=broad-except
        print(error)
        return
    try:
        print("Enable All Users Test: ", await enable_all_user(panel_data))
    except Exception as error:  # pylint: disable=broad-except
        print(error)
        return
    try:
        print(
            "Disable User Test: ",
            await disable_user(
                panel_data,
                users[0],
            ),
        )
        print(
            "Disable User Test: ",
            await disable_user(
                panel_data,
                users[1],
            ),
        )
    except Exception as error:  # pylint: disable=broad-except
        print(error)
        return
    print(
        "Enable selected Users Test: ",
        await enable_selected_users(panel_data, set([users[0].name, users[1].name])),
    )
    print("Get Nodes Test: ", await get_nodes(panel_data))
    async with asyncio.TaskGroup() as tg:
        print("Start Create Panel Task Test: ")
        await create_panel_task(panel_data, tg)
        await asyncio.sleep(5)
        print("Cancel Panel Task Test: ")
        await handle_cancel_one(TASKS)
    nodes_list = await get_nodes(panel_data)
    async with asyncio.TaskGroup() as tg:
        if nodes_list and not isinstance(nodes_list, ValueError):
            print("Start Create Nodes Task Test: ")
            for node in nodes_list:
                await create_node_task(panel_data, tg, node)
                await asyncio.sleep(2)
            await asyncio.sleep(20)
            # pylint: disable=duplicate-code
            print("Start 'check_and_add_new_nodes' Task Test: ")
            tg.create_task(
                check_and_add_new_nodes(panel_data, tg),
                name="add_new_nodes",
            )
            print("Start 'handle_cancel' Task Test: ")
            tg.create_task(
                handle_cancel(panel_data, TASKS),
                name="cancel_disable_nodes",
            )
        tg.create_task(
            enable_dis_user(panel_data),
            name="enable_dis_user",
        )
        ACTIVE_USERS.clear()
        await add_fake_users()
        await run_check_users_usage(panel_data)


if __name__ == "__main__":
    if (
        input(
            "This is test file and it may break your data. So if you want to continue Enter y: "
        )
        == "y"
    ):
        asyncio.run(main())
