import asyncio
from typing import Coroutine, Union

from interactions.api.models.misc import MISSING, Snowflake
from interactions.client.bot import Client
from interactions.client.models.command import ApplicationCommand
from interactions.client.models.component import Button, Modal, SelectMenu

from .dummy import _Client


class ShardedClient(Client):
    def __init__(self, token: str, shard_count: int = MISSING, **kwargs):
        super().__init__(token, **kwargs)
        self.shards = []
        self._clients = []
        if shard_count and shard_count != MISSING and isinstance(shard_count, int):
            self._shard_count = shard_count
        else:
            self._shard_count = self._loop.run_until_complete(self._get_shard_count())
        self.generate_shard_list()

        for shard in self.shards:
            if not self._clients:
                _client = Client(token, shards=shard, **kwargs)
            else:
                _guild = self.clients[0]._Client__guild_commands
                _global = self._clients[0]._Client__global_commands
                _client = _Client(
                    token, guild_cmds=_guild, global_cmds=_global, disable_sync=True, **kwargs
                )
            self._clients.append(_client)

    async def _get_shard_count(self) -> int:
        data = await self._http.get_bot_gateway()
        return data[0]

    def generate_shard_list(self) -> None:
        """
        Generates a list of shards.
        """
        for shard in range(self._shard_count):
            self.shards.append([shard, self._shard_count])

    async def _login(self) -> None:

        _funcs = [self._loop.create_task(client._ready()) for client in self._clients]
        gathered = asyncio.gather(*_funcs)
        while not self._websocket._closed:
            await gathered

    def command(
        self,
        **kwargs,
    ):
        def decorator(coro: Coroutine):
            for client in self._clients:
                if client == self._clients[0]:
                    continue
                client.command(**kwargs)(coro)

            return self._clients[0].command(**kwargs)(coro)

        return decorator

    def message_command(
        self,
        **kwargs,
    ):
        def decorator(coro: Coroutine):
            for client in self._clients:
                if client == self._clients[0]:
                    continue
                client.message_command(**kwargs)(coro)
            return self._clients[0].message_command(**kwargs)(coro)

        return decorator

    def user_command(
        self,
        **kwargs,
    ):
        def decorator(coro: Coroutine):
            for client in self._clients:
                if client == self._clients[0]:
                    continue
                client.user_command(**kwargs)(coro)
            return self._clients[0].user_command(**kwargs)(coro)

        return decorator

    def component(self, component: Union[Button, SelectMenu, str]):
        def decorator(coro: Coroutine):
            for client in self._clients:
                if client == self._clients[0]:
                    continue
                client.component(component)(coro)
            return self._clients[0].component(component)(coro)

        return decorator

    def autocomplete(self, command: Union[ApplicationCommand, int, str, Snowflake], name: str):
        def decorator(coro: Coroutine) -> None:
            for client in self._clients:
                if client == self._clients[0]:
                    continue
                client.autocomplete(command, name)(coro)
            return self._clients[0].autocomplete(command, name)(coro)

        return decorator

    def modal(self, modal: Union[Modal, str]):
        def decorator(coro: Coroutine) -> None:
            for client in self._clients:
                if client == self._clients[0]:
                    continue
                client.modal(modal)(coro)
            return self._clients[0].modal(modal)(coro)

        return decorator
