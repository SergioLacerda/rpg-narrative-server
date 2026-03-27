import time
import asyncio


class MessageRuntime:

    def __init__(self):
        self.last_user_message = {}
        self.last_channel_warning = {}
        self.channel_locks = {}

    def check_cooldown(self, user_id: str, seconds: int) -> bool:
        now = time.time()
        last = self.last_user_message.get(user_id, 0)

        if now - last < seconds:
            return False

        self.last_user_message[user_id] = now
        return True

    def should_warn(self, channel_id: str, debounce: int) -> bool:
        now = time.time()
        last = self.last_channel_warning.get(channel_id, 0)

        if now - last < debounce:
            return False

        self.last_channel_warning[channel_id] = now
        return True

    def get_lock(self, channel_id: str):
        if channel_id not in self.channel_locks:
            self.channel_locks[channel_id] = asyncio.Lock()
        return self.channel_locks[channel_id]