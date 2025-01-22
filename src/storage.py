import asyncio

from user import User

class Storage:
    def __init__(self):
        self.users = {}
        self.lock = asyncio.Lock()

    async def create_user(self, uid):
        async with self.lock:
            if uid in self.users:
                return False
            self.users[uid] = User(uid)
        return True

    async def delete_user(self, uid):
        async with self.lock:
            if uid not in self.users:
                return False
            del self.users[uid]
        return True

    async def apply(self, uid, func):
        async with self.lock:
            if uid not in self.users:
                raise ValueError(f"User {uid} not in storage!")
            return await func(self.users[uid])

    async def exists(self, uid):
        async with self.lock:
            return uid in self.users
