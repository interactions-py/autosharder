# interactions-autosharder
____________________________
[!downloads](https://img.shields.io/pypi/dm/interactions-autosharder?color=blue&style=for-the-badge)
You wanted to use `interactions.py` but were afraid of the lack of sharding? Or you did manual sharding but it sucks?
Well, this will help you out! Install via `pip install interactions-autosharder` and do this in your main file:

```python
from interactions.ext.autosharder import ShardedClient

bot = ShardedClient("the_arguments_you_gave_the_normal_client")
```
It will automatically get the needed shard count and create the shards. Optionally, insert the `shard_count` parameter
and set it to the amount of shards you want!


## Extensions
______________
Extensions are still usable with the autosharded client, but you will have to subclass from ``ShardedExtension``.
You can import it via ``from interactions.ext.autosharder import ShardedExtension``
