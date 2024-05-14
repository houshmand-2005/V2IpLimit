import asyncio
from asyncio import Task
from ssl import SSLError

import websockets.client

from utils.logs import logger
from utils.panel_api import get_nodes, get_token
from utils.parse_logs import parse_logs
from utils.types import NodeType, PanelType

TASKS = []


async def get_panel_logs(panel_data: PanelType) -> None:
    """
    This function establishes a websocket connection to the main server and retrieves logs.

    Args:
        panel_data (PanelType): The credentials for the panel.

    Raises:
        ValueError: If there is an issue with getting the panel token.
    """
    get_panel_token = await get_token(panel_data)
    if isinstance(get_panel_token, ValueError):
        raise get_panel_token
    token = get_panel_token.panel_token
    for scheme in ["wss", "ws"]:
        while True:
            try:
                async with websockets.client.connect(
                    f"{scheme}://{panel_data.panel_domain}/api/core/logs?interval=0.7&token={token}"
                ) as ws:
                    logger.info("Establishing connection main server")
                    while True:
                        new_log = await ws.recv()
                        await parse_logs(new_log)

            except SSLError:
                break
            except Exception as error:
                logger.error(
                    "[Main panel] Failed to connect %s trying 20 secned later!", error
                )
                await asyncio.sleep(20)
                continue


async def get_nodes_logs(panel_data: PanelType, node: NodeType) -> None:
    """
    This function establishes a websocket connection to a specific node and retrieves logs.

    Args:
        panel_data (PanelType): The credentials for the panel.
        node (NodeType): The specific node to connect to.

    Raises:
        ValueError: If there is an issue with getting the panel token.
    """
    get_panel_token = await get_token(panel_data)
    if isinstance(get_panel_token, ValueError):
        raise get_panel_token
    token = get_panel_token.panel_token
    for scheme in ["ws", "wss"]:
        while True:
            try:
                async with websockets.client.connect(
                    f"{scheme}://{panel_data.panel_domain}/api/node/{node.node_id}/logs?interval=0.7&token={token}"
                ) as ws:
                    logger.info(
                        "Establishing connection for node number %s", node.node_id
                    )
                    while True:
                        new_log = await ws.recv()
                        await parse_logs(new_log)
            except SSLError:
                break
            except Exception:
                logger.error(
                    "[node id: %s] [node name: %s] [node ip: %s] [node status: %s] [node message: %s]",
                    node.node_id,
                    node.node_name,
                    node.node_ip,
                    node.status,
                    node.message,
                )
                await asyncio.sleep(20)
                continue


async def handle_cancel(tasks: list[Task], nodes_list: list[NodeType]) -> None:
    """
    An asynchronous coroutine that cancels all tasks in the given list.

    Args:
        tasks (list[Task]): The list of tasks to be cancelled.
        nodes_list (list[NodeType]): The list of nodes to be checked for deactive nodes.
    """
    deactive_nodes = set()
    while True:
        for node in nodes_list:
            if node.status != "active":
                deactive_nodes.add(f"Task-{node.node_id}")

        for task in tasks:
            if task.get_name() in deactive_nodes:
                logger.info("Cancelling %s", task.get_name())
                deactive_nodes.remove(task.get_name())
                task.cancel()
                tasks.remove(task)
        await asyncio.sleep(17)


async def handle_cancel_one(tasks: list[Task]) -> None:
    """
    *This is used for tests*
    An asynchronous coroutine that cancels just one tasks in the given list.

    Args:
        tasks (list[Task]): The list of tasks to be cancelled.
    """
    for task in tasks:
        print(task)
        if task.get_name() == "Task-panel":
            print(f"Cancelling {task.get_name()}...")
            task.cancel()
            tasks.remove(task)


async def check_and_add_new_nodes(
    panel_data: PanelType, tg: asyncio.TaskGroup, existing_nodes: list[NodeType]
) -> None:
    """
    An asynchronous coroutine that checks for new nodes and creates tasks for them.

    Args:
        panel_data (PanelType): The credentials for the panel.
        tg (asyncio.TaskGroup): The TaskGroup to which the new task will be added.
        existing_nodes (list[NodeType]): The list of existing nodes.
    """
    while True:
        all_nodes = await get_nodes(panel_data)
        if all_nodes and not isinstance(all_nodes, ValueError):
            for node in all_nodes:
                if node not in existing_nodes:
                    logger.info(
                        "Add a new node. id: %s name %s ip: %s",
                        node.node_id,
                        node.node_name,
                        node.node_ip,
                    )
                    existing_nodes.append(node)
                    await create_node_task(panel_data, tg, node)
        await asyncio.sleep(10)


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
    TASKS.append(
        tg.create_task(get_nodes_logs(panel_data, node), name=f"Task-{node.node_id}"),
    )
