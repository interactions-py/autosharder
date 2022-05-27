# interactions-autosharder
____________________________

You wanted to use `interactions.py` but were afraid of the lack of sharding? Or you did manual sharding but it sucks?
Well, this will help you out! Install via `pip install interactions-autosharder` and do this in your main file:

```python
from interactions.ext.autosharder import ShardedClient

bot = ShardedClient("the_arguments_you_gave_the_normal_client")
```
It will automatically get the needed shard count and create the shards. Optionally, insert the `shard_count` parameter
and set it to the amount of shards you want!
