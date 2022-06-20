from interactions.client.bot import Client
from typing import Any, Callable, Dict, List, Optional, Union

from interactions.api import Item as Build
from interactions.api import WebSocketClient as WSClient
from interactions.api.models.flags import Permissions
from interactions.api.models.guild import Guild
from interactions.api.models.misc import MISSING, Snowflake
from interactions.client.decor import component as _component
from interactions.client.enums import ApplicationCommandType, Locale
from interactions.client.models.command import ApplicationCommand, Option
from interactions.client.models.component import Button, Modal, SelectMenu
from .dummy import _Client

class ShardedClient(Client):
    _clients: List[Client, _Client]
    _shard_count: int
    shards: List[List[int, int]]
    def __init__(self, token: str, shard_count: int = MISSING, **kwargs): ...
    async def _get_shard_count(self) -> int: ...
    def generate_shard_list(self) -> None: ...
    async def _login(self) -> None: ...
    async def _ready(self) -> None: ...
    def latency(self) -> float: ...
    def command(
        self,
        *,
        type: Optional[Union[str, int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        options: Optional[List[Option]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        description_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
        dm_permission: Optional[bool] = MISSING
    ) -> Callable[..., Any]: ...
    def message_command(
        self,
        *,
        name: str,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
        dm_permission: Optional[bool] = MISSING
    ) -> Callable[..., Any]: ...
    def user_command(
        self,
        *,
        name: str,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        name_localizations: Optional[Dict[Union[str, Locale], str]] = MISSING,
        default_member_permissions: Optional[Union[int, Permissions]] = MISSING,
        dm_permission: Optional[bool] = MISSING
    ) -> Callable[..., Any]: ...
    def component(self, component: Union[Button, SelectMenu, str]) -> Callable[..., Any]: ...
    def autocomplete(
        self, command: Union[ApplicationCommand, int, str, Snowflake], name: str
    ) -> Callable[..., Any]: ...
    def modal(self, modal: Union[Modal, str]) -> Callable[..., Any]: ...
