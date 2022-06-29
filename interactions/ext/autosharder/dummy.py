import itertools
from asyncio import gather
from typing import List

from interactions.api.models.flags import Intents
from interactions.base import get_logger
from interactions.client.bot import Client

__all__ = ("DummyClient", "MethodReplacer")


class DummyClient(Client):
    """
    This class is representing a dummy without sync behaviour, handling a shard without getting
    commands or making extra sync calls. Do not use this class.
    """

    def __init__(self, token, **kwargs):
        super().__init__(token, **kwargs)

    async def _ready(self) -> None:
        log = get_logger("Client")
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

            await self._Client__get_all_commands()
            # await self.__register_name_autocomplete()
            # self.__register_events()

            # no dispatch things here

            ready = True
        except Exception:
            log.exception("Could not prepare the client:")
        finally:
            if ready:
                log.debug("Client is now ready.")
                await self._login()


class MethodReplacer(Client):
    def __init__(self, token: str, **kwargs):
        super().__init__(token, **kwargs)
        self._clients: List[DummyClient] = []

    async def __sync(self) -> None:
        await super()._Client__sync()

    def start(self):
        if self._automate_sync:
            self._loop.run_until_complete(self.__sync())
            self._automate_sync = False
        self._loop.run_until_complete(self.__ready())

    async def _ready(self) -> None:
        await self._login()

    async def __ready(self) -> None:
        ready: bool = False
        log = get_logger("Client")
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

            self._Client__register_events()

            await self._Client__register_name_autocomplete()

            ready = True
        except Exception:
            log.exception("Could not prepare the client:")
        finally:
            if ready:
                log.debug("Client is now ready.")
                await self.__login()

    async def __login(self) -> None:

        for attrib, client in itertools.product(self._websocket._dispatch.__slots__, self._clients):
            setattr(client._websocket._dispatch, attrib, getattr(self._websocket._dispatch, attrib))

        if len(self._clients) <= 15:
            tasks = [self._ready()]
            tasks.extend(client._ready() for client in self._clients)

            gathered = gather(*tasks)
            await gathered
