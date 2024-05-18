"""
This module contains the data classes used in the application.
"""

from dataclasses import dataclass, field
from enum import Enum


@dataclass
class PanelType:
    """
    A class used to represent the credentials for a panel.

    Attributes:
        panel_username (str): The username for the panel.
        panel_password (str): The password for the panel.
        panel_domain (str): The domain for the panel.
        panel_token (Optional[str]): The token for the panel. None if no token is provided.
    """

    panel_username: str
    panel_password: str
    panel_domain: str
    panel_token: str | None = None


@dataclass
class NodeType:
    """
    A class used to represent the data for a node.

    Attributes:
        node_id (int): The ID of the node.
        node_name (str): The name of the node.
        node_ip (str): The IP address of the node.
        status (str): The status of the node.
        message (str): The message of the node.
    """

    node_id: int
    node_name: str
    node_ip: str
    status: str
    message: str | None = None


class UserStatus(Enum):
    """
    Enum representing the type of UserStatus.

    Attributes:
        ACTIVE (str)
        DISABLE (str)
    """

    ACTIVE = "ACTIVE"
    DISABLE = "DISABLE"


@dataclass
class UserType:
    """
    Represents a user type.

    Attributes:
        name (str): The name of the user.
        status (str | None): The status of the user. None if no status is provided.
        ip (list[str] | list): List of IP address of the user.
    """

    name: str
    status: UserStatus | None = None
    ip: list[str] | list = field(default_factory=list)
