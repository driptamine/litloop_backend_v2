# Troubleshooting

## WebSocket / Daphne

### `__init__() got an unexpected keyword argument 'connection_options'`

**Cause:** `channels_redis` version does not support `connection_options` in `CHANNEL_LAYERS.CONFIG`.

**Check:**
```bash
# See what params RedisChannelLayer actually accepts
venv_3.9/bin/python -c "
import channels_redis.core, inspect
print(inspect.signature(channels_redis.core.RedisChannelLayer.__init__))
"
```

**Fix:** Remove `connection_options` from `litloop_project/settings/base.py`:
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_LOCATION],  # connection_options removed
        },
    },
}
```

---

### WebSocket connection fails (browser shows "failed")

**1. Check if daphne is running:**
```bash
ps aux | grep daphne
```

**2. Check server logs:**
```bash
tail -f /tmp/daphne.log
```

**3. Restart daphne after code changes:**
```bash
# Find PID from ps output, then:
kill <PID>

# Restart:
cd /path/to/project
nohup venv_3.9/bin/daphne -p 8000 litloop_project.asgi:application > /tmp/daphne.log 2>&1 &
```

> Python caches modules in memory — editing a file does NOT affect a running process. You must restart daphne.

**4. Test WebSocket directly (without frontend):**
```bash
venv_3.9/bin/python -c "
import asyncio, websockets
async def t():
    try:
        async with websockets.connect('ws://localhost:8000/ws/chat/1/?token=test') as ws:
            print('Connected')
            print(await ws.recv())
    except Exception as e:
        print(f'Failed: {e}')
asyncio.run(t())
"
```
