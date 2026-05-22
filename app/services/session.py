import time
import json

from redis.asyncio import Redis
from user_agents import parse

from app.core.security import generate_session_id
from app.core.config import settings



class SessionService:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    @staticmethod
    def parse_user_agent(user_agent: str|None) -> dict:
        if not user_agent:
            return {}
        ua = parse(user_agent)
        return {
            "browser": ua.browser.family ,
            "os": ua.os.family,
            "device": ua.device.family,
            "is_mobile": ua.is_mobile,
        }

    async def create_session(
            self,
            user_id: int,
            ip: str | None,
            user_agent: str | None,
    ) -> str:
        session_id = generate_session_id()

        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "ip": ip,
            "created_at": int(time.time()),
            **self.parse_user_agent(user_agent),
        }

        await self._redis.setex(
            f"{settings.REDIS_SESSION_PREFIX}{session_id}",
            settings.SESSION_TTL,
            json.dumps(payload),
        )

        user_sessions_key = f"{settings.REDIS_USER_SESSION_PREFIX}:{user_id}"
        await self._redis.sadd(user_sessions_key, session_id)
        await self._redis.expire(user_sessions_key, settings.SESSION_TTL)

        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        raw = await self._redis.get(
            f"{settings.REDIS_SESSION_PREFIX}{session_id}"
        )

        if not raw:
            return None

        return json.loads(raw)

    async def invalidate_session(self, session_id: str) -> None:
        data = await self.get_session(session_id)
        if data:
            await self._redis.srem(f"{settings.REDIS_USER_SESSION_PREFIX}:{data['user_id']}", session_id)

        await self._redis.delete(
            f"{settings.REDIS_SESSION_PREFIX}{session_id}"
        )

    async def get_active_sessions(
            self,
            user_id: int,
            offset: int = 0,
            limit: int = 10
    ) -> list[dict]:
        user_sessions_key = f"{settings.REDIS_USER_SESSION_PREFIX}:{user_id}"
        session_ids = await self._redis.smembers(user_sessions_key)

        sessions = []
        for sid in session_ids:
            sid_str = sid.decode("utf-8") if isinstance(sid, bytes) else sid
            data = await self.get_session(sid_str)
            if data:
                sessions.append(data)
            else:
                await self._redis.srem(user_sessions_key, sid_str)

        sessions.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return sessions[offset: offset + limit]

