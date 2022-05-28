import asyncio
from typing import Coroutine, Union

from interactions.api.models.misc import MISSING, Snowflake
from interactions.client.bot import Client
from interactions.client.models.command import ApplicationCommand
from interactions.client.models.component import Button, Modal, SelectMenu


class _Client(Client):
    """This class is representing a dummy without sync behaviour, handling a shard without getting commands or making extra sync calls. Do not use this class."""

    def __init__(self, token, guild_cmds, global_cmds, **kwargs):
        super().__init__(token, **kwargs)
        self.__guild_commands = guild_cmds
        self.__global_commands = global_cmds

    async def _ready(self) -> None:
        ready: bool = False

        try:
            if self.me.flags is not None:
                # This can be None.
                if self._intents.GUILD_PRESENCES in self._intents and not (
                    self.me.flags.GATEWAY_PRESENCE in self.me.flags
                    or self.me.flags.GATEWAY_PRESENCE_LIMITED in self.me.flags
                ):
                    raise RuntimeError("Client not authorised for the GUILD_PRESENCES intent.")
                if self._intents.GUILD_MEMBERS in self._intents and not (
                    self.me.flags.GATEWAY_GUILD_MEMBERS in self.me.flags
                    or self.me.flags.GATEWAY_GUILD_MEMBERS_LIMITED in self.me.flags
                ):
                    raise RuntimeError("Client not authorised for the GUILD_MEMBERS intent.")
                if self._intents.GUILD_MESSAGES in self._intents and not (
                    self.me.flags.GATEWAY_MESSAGE_CONTENT in self.me.flags
                    or self.me.flags.GATEWAY_MESSAGE_CONTENT_LIMITED in self.me.flags
                ):
                    log.critical("Client not authorised for the MESSAGE_CONTENT intent.")
            elif self._intents.value != Intents.DEFAULT.value:
                raise RuntimeError("Client not authorised for any privileged intents.")

            self.__register_events()

            if self._automate_sync:
                await self.__sync()
            else:
                await self.__get_all_commands()
            await self.__register_name_autocomplete()

            ready = True
        except Exception:
            log.exception("Could not prepare the client:")
        finally:
            if ready:
                log.debug("Client is now ready.")
                await self._login()


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
            if len(self._clients) == 0:
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
