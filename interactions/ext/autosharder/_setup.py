from interactions.client.bot import Client, Extension

__all__ = "setup, setup_extension"


def setup(_client: Client):
    ...


def setup_extension(_extension: Extension):
    ...
