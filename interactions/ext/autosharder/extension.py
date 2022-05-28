from asyncio import iscoroutinefunction
from inspect import getmembers
from typing import Union

from interactions.api.models.misc import Snowflake
from interactions.client.decor import component as _component
from interactions.client.models.command import ApplicationCommand
from interactions.client.models.component import Button, Modal, SelectMenu

from .client import ShardedClient


class ShardedExtension:
    """
    A class that allows you to represent "extensions" of your code, or
    essentially cogs that can be ran independent of the root file in
    an object-oriented structure.

    The structure of an extension:

    .. code-block:: python

        class CoolCode(ShardedExtension):
            def __init__(self, client):
                self.client = client

            @extension_command(
                type=interactions.ApplicationCommandType.USER,
                name="User command in cog",
            )
            async def cog_user_cmd(self, ctx):
                ...

        def setup(client):
            CoolCode(client)
    """

    client: ShardedClient

    def __new__(cls, client: ShardedClient, *args, **kwargs) -> "ShardedExtension":

        self = super().__new__(cls)

        self.client = client
        self._commands = {}
        self._listeners = {}

        # This gets every coroutine in a way that we can easily change them
        # cls
        for name, func in getmembers(self, predicate=iscoroutinefunction):
            if hasattr(func, "__listener_name__"):  # set by extension_listener
                for _client in self.client._clients:
                    if self.client._clients[0] == _client:
                        func = _client.event(
                            func, name=func.__listener_name__
                        )  # capture the return value for friendlier ext-ing
                    else:
                        _client.event(func, name=func.__listener_name__)

                listeners = self._listeners.get(func.__listener_name__, [])
                listeners.append(func)
                self._listeners[func.__listener_name__] = listeners

            if hasattr(func, "__command_data__"):  # Set by extension_command
                args, kwargs = func.__command_data__
                for _client in self.client._clients:
                    if self.client._clients[0] == client:
                        func = _client.command(*args, **kwargs)(func)
                    else:
                        _client.command(*args, **kwargs)(func)

                cmd_name = f"command_{kwargs.get('name') or func.__name__}"

                commands = self._commands.get(cmd_name, [])
                commands.append(func)
                self._commands[cmd_name] = commands

            if hasattr(func, "__component_data__"):
                args, kwargs = func.__component_data__
                for _client in self.client._clients:
                    if self.client._clients[0] == client:
                        func = _client.component(*args, **kwargs)(func)
                    else:
                        _client.component(*args, **kwargs)(func)

                component = kwargs.get("component") or args[0]
                comp_name = (
                    _component(component).custom_id
                    if isinstance(component, (Button, SelectMenu))
                    else component
                )
                comp_name = f"component_{comp_name}"

                listeners = self._listeners.get(comp_name, [])
                listeners.append(func)
                self._listeners[comp_name] = listeners

            if hasattr(func, "__autocomplete_data__"):
                args, kwargs = func.__autocomplete_data__
                for _client in self.client._clients:
                    if self.client._clients[0] == client:
                        func = _client.autocomplete(*args, **kwargs)(func)
                    else:
                        _client.autocomplete(*args, **kwargs)(func)

                name = kwargs.get("name") or args[0]
                _command = kwargs.get("command") or args[1]

                _command: Union[Snowflake, int] = (
                    _command.id if isinstance(_command, ApplicationCommand) else _command
                )

                auto_name = f"autocomplete_{_command}_{name}"

                listeners = self._listeners.get(auto_name, [])
                listeners.append(func)
                self._listeners[auto_name] = listeners

            if hasattr(func, "__modal_data__"):
                args, kwargs = func.__modal_data__
                for _client in self.client._clients:
                    if self.client._clients[0] == client:
                        func = _client.modal(*args, **kwargs)(func)
                    else:
                        _client.modal(*args, **kwargs)(func)

                modal = kwargs.get("modal") or args[0]
                _modal_id: str = modal.custom_id if isinstance(modal, Modal) else modal
                modal_name = f"modal_{_modal_id}"

                listeners = self._listeners.get(modal_name, [])
                listeners.append(func)
                self._listeners[modal_name] = listeners

        client._extensions[cls.__name__] = self

        if client._clients[0]._websocket.ready.is_set() and client._clients[0]._automate_sync:
            client._loop.create_task(client._clients[0]._Client__sync())

        return self

    async def teardown(self):
        for event, funcs in self._listeners.items():
            for func in funcs:
                for _client in self.client._clients:
                    _client._websocket._dispatch.events[event].remove(func)

        for cmd, funcs in self._commands.items():
            for func in funcs:
                for _client in self.client._clients:
                    _index = _client._Client__command_coroutines.index(func)
                    _client._Client__command_coroutines.pop(_index)
                    _client._websocket._dispatch.events[cmd].remove(func)

        if self.client._automate_sync:
            await self.client._clients[0]._Client__sync()
