"""
This module contains functions to get logs from the panel and nodes.
"""

import asyncio
import random
import ssl
import sys
from asyncio import Task
from ssl import SSLError

from utils.parse_logs import INVALID_IPS

try:
    import websockets.client
except ImportError:
    print(
        "Module 'websockets' is not installed use: 'pip install websockets' to install it"
    )
    sys.exit()
from telegram_bot.send_message import send_logs
from utils.logs import logger  # pylint: disable=ungrouped-imports
from utils.panel_api import get_nodes, get_token
from utils.parse_logs import parse_logs
from utils.types import NodeType, PanelType

TASKS = []

import os
import re
from datetime import datetime, timedelta

# مسیر فایل ذخیره لاگ فیلتر شده
LOG_FILE_PATH = "/root/V2IpLimit/connections_log.txt"

def save_filtered_log(log_data):
    """ذخیره لاگ‌های دارای email همراه با زمان دقیق تهران."""
    try:
        # جستجوی خطوطی که حاوی email هستند
        match = re.search(r"accepted tcp:([\w\.-]+):\d+.*email: ([\w\.]+)", log_data)
        if match:
            destination, email = match.groups()

            # دریافت ساعت تهران (UTC+3:30)
            tehran_time = datetime.utcnow() + timedelta(hours=3, minutes=30)
            formatted_time = tehran_time.strftime("%Y-%m-%d %H:%M:%S")

            # ذخیره در فایل لاگ با زمان تهران
            log_entry = f"{formatted_time} - {email} connected to {destination}\n"

            with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(log_entry)
    except Exception as e:
        print(f"⚠️ Error saving filtered log: {e}")



task_node_mapping = {}
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def get_panel_logs(panel_data: PanelType) -> None:
    for scheme in ["wss", "ws"]:
        while True:
            interval = random.choice(("0.9", "1.3", "1.5", "1.7"))
            get_panel_token = await get_token(panel_data)
            if isinstance(get_panel_token, ValueError):
                raise get_panel_token
            token = get_panel_token.panel_token
            try:
                async with websockets.client.connect(
                    f"{scheme}://{panel_data.panel_domain}/api/core"
                    + f"/logs?interval={interval}&token={token}",
                    ssl=ssl_context if scheme == "wss" else None,
                    ping_interval=20,    # ← اضافه شد
                    ping_timeout=20,     # ← اضافه شد
                ) as ws:

                    log_message = "Establishing connection for the main panel"
                    await send_logs(log_message)
                    logger.info(log_message)
                    while True:
                        new_log = await ws.recv()
                        await parse_logs(str(new_log))
                        save_filtered_log(new_log)  # ذخیره فقط لاگ‌های دارای email


            except SSLError:
                break
            except Exception as error:
                log_message = f"[Main panel] Failed to connect {error} trying 20 second later!"
                await send_logs(log_message)
                logger.error(log_message)
                await asyncio.sleep(20)
                continue



async def get_nodes_logs(panel_data: PanelType, node: NodeType) -> None:
    for scheme in ["wss", "ws"]:
        while True:
            interval = random.choice(("0.9", "1.3", "1.5", "1.7"))
            get_panel_token = await get_token(panel_data)
            if isinstance(get_panel_token, ValueError):
                raise get_panel_token
            token = get_panel_token.panel_token
            try:
                url = f"{scheme}://{panel_data.panel_domain}/api/node/{node.node_id}/logs?interval={interval}&token={token}"
                async with websockets.client.connect(
                    url,
                    ssl=ssl_context if scheme == "wss" else None,
                    ping_interval=20,    # ← اضافه شد
                    ping_timeout=20,     # ← اضافه شد
                    
                ) as ws:

                    log_message = (
                        f"Establishing connection for node number {node.node_id} name: {node.node_name}"
                    )
                    await send_logs(log_message)
                    logger.info(log_message)
                    while True:
                        new_log = await ws.recv()
                        await parse_logs(str(new_log))
                        save_filtered_log(new_log)  # ذخیره فقط لاگ‌های دارای email



            except SSLError:
                break
            except Exception as error:
                log_message = (
                    f"Failed to connect to this node [node id: {node.node_id}]"
                    + f" [node name: {node.node_name}]"
                    + f" [node ip: {node.node_ip}] [node message: {node.message}]"
                    + f" [Error Message: {error}] trying to connect 10 second later!"
                )
                await send_logs(log_message)
                logger.error(log_message)
                await asyncio.sleep(10)
                continue



async def handle_cancel(panel_data: PanelType, tasks: list[Task]) -> None:
    """
    An asynchronous coroutine that cancels all tasks in the given list.

    Args:
        panel_data (PanelType): The credentials for the panel.
        tasks (list[Task]): The list of tasks to be cancelled.
    """
    deactivate_nodes = set()
    while True:
        nodes_list = await get_nodes(panel_data)
        for node in nodes_list:
            if node.status != "connected":
                deactivate_nodes.add(f"Task-{node.node_id}-{node.node_name}")

        for task in tasks:
            if task.get_name() in deactivate_nodes:
                log_message = f"Cancelling {task.get_name()}"
                await send_logs(log_message)
                logger.info(log_message)
                deactivate_nodes.remove(task.get_name())
                task.cancel()
                tasks.remove(task)
                if task in task_node_mapping:
                    task_node_mapping.pop(task)
        await asyncio.sleep(20)


async def handle_cancel_one(tasks: list[Task]) -> None:
    """
    *This is used for tests*
    An asynchronous coroutine that cancels just one tasks in the given list.

    Args:
        tasks (list[Task]): The list of tasks to be cancelled.
    """
    for task in tasks:
        if task.get_name() == "Task-panel":
            print(f"Cancelling {task.get_name()}...")
            task.cancel()
            tasks.remove(task)


async def handle_cancel_all(tasks: list[Task], panel_data: PanelType) -> None:
    """
    An asynchronous coroutine that cancels All tasks in the given list.
    To fix these issues: #67, #65, #62 And many more

    Args:
        tasks (list[Task]): The list of tasks to be cancelled.
    """
    # pylint: disable=duplicate-code
    async with asyncio.TaskGroup() as tg:
        while True:
            await asyncio.sleep(8192)  # =~ 2 hours and 27 minutes
            for task in tasks:
                print(f"Cancelling {task.get_name()}...")
                task.cancel()
                tasks.remove(task)
            print("Start Create Panel Task Test: ")
            await create_panel_task(panel_data, tg)
            await asyncio.sleep(5)
            nodes_list = await get_nodes(panel_data)
            if nodes_list and not isinstance(nodes_list, ValueError):
                print("Start Create Nodes Task Test: ")
                for node in nodes_list:
                    if node.status == "connected":
                        await create_node_task(panel_data, tg, node)
                        await asyncio.sleep(3)


async def check_and_add_new_nodes(panel_data: PanelType, tg: asyncio.TaskGroup) -> None:
    """
    An asynchronous coroutine that checks for new nodes and creates tasks for them.

    Args:
        panel_data (PanelType): The credentials for the panel.
        tg (asyncio.TaskGroup): The TaskGroup to which the new task will be added.
    """
    while True:
        all_nodes = await get_nodes(panel_data)
        if all_nodes and not isinstance(all_nodes, ValueError):
            for node in all_nodes:
                if (
                    node not in task_node_mapping.values()
                    and node.status == "connected"
                ):
                    log_message = (
                        f"Add a new node. id: {node.node_id}"
                        + f" name: {node.node_name} ip: {node.node_ip}"
                    )
                    await send_logs(log_message)
                    logger.info(log_message)
                    await create_node_task(panel_data, tg, node)
        await asyncio.sleep(25)


async def create_panel_task(panel_data: PanelType, tg: asyncio.TaskGroup) -> None:
    """
    An asynchronous coroutine that creates a new task for a node and adds it to the TASKS list.

    Args:
        panel_data (PanelType): The credentials for the panel.
        tg (asyncio.TaskGroup): The TaskGroup to which the new task will be added.
    """
    TASKS.append(
        tg.create_task(get_panel_logs(panel_data), name="Task-panel"),
    )


async def create_node_task(
    panel_data: PanelType, tg: asyncio.TaskGroup, node: NodeType
) -> None:
    """
    An asynchronous coroutine that creates a new task for a node and adds it to the TASKS list.

    Args:
        panel_data (PanelType): The credentials for the panel.
        tg (asyncio.TaskGroup): The TaskGroup to which the new task will be added.
        node (NodeType): The node for which the new task will be created.
    """
    INVALID_IPS.add(node.node_ip)
    task = tg.create_task(
        get_nodes_logs(panel_data, node), name=f"Task-{node.node_id}-{node.node_name}"
    )
    TASKS.append(task)
    task_node_mapping[task] = node
