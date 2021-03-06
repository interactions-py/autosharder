from typing import List, Optional
from asyncio import gather
from interactions.client.bot import Client, Extension


class DummyClient(Client):
    def __init__(self, token: str, **kwargs) -> None: ...
    async def _ready(self) -> None: ...

class AutoShardedClient(Client):
    _clients: List[DummyClient] = []
    gather_tasks: List[gather]
    def __init__(self, token: str, **kwargs) -> None: ...
    @property
    def total_latency(self) -> float: ...
    def start(self) -> None: ...
    async def _login(self) -> None: ...
    async def __login(self) -> None: ...
    async def __ready(self) -> None: ...
    async def _ready(self) -> None: ...
    def run_gathered(self) -> None: ...
    def remove(self, name: str, package: Optional[str] = None) -> None: ...
    def load(
        self, name: str, package: Optional[str] = None, *args, **kwargs
    ) -> Optional[Extension]: ...
