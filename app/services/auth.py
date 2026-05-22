import json

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import generate_otp, verify_password
from app.cruds.admin_user import AdminUserCrud
from app.services.mail import mailer

from app.exceptions.auth import InvalidCredentialsError, InvalidOTPError, AccountInactiveError, TooManyAuthRequests
from app.db.models import AdminUser
from app.exceptions.auth import SessionExpiredError
from app.services.session import SessionService


class AuthService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.crud = AdminUserCrud(session)
        self._redis = redis
        self.session_service = SessionService(redis)

    async def _check_rate_limit(self, email: str) -> None:
        key = f"{settings.REDIS_RATE_LIMIT_PREFIX}:{email}"
        attempts = await self._redis.incr(key)

        if attempts == 1:
            await self._redis.expire(key, settings.RATE_LIMIT_RESET_TIME)

        if attempts > 3:
            raise TooManyAuthRequests()

    async def initiate_login(self, email: str, password: str) -> None:
        await self._check_rate_limit(email)

        user = await self.crud.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise AccountInactiveError()

        otp = generate_otp()
        payload = json.dumps(
            {
                "otp": otp
            }
        )
        await self._redis.setex(f"{settings.REDIS_OTP_PREFIX}{email}", settings.OTP_TTL, payload)
        await mailer.send_otp_email(email, otp)
        

    async def verify_otp(self, email: str, otp: str, ip: str|None, user_agent: str|None) -> str:
        raw = await self._redis.get(f"{settings.REDIS_OTP_PREFIX}{email}")
        if not raw:
            raise InvalidOTPError()

        data = json.loads(raw)
        if data["otp"] != otp:
            raise InvalidOTPError()

        await self._redis.delete(f"{settings.REDIS_OTP_PREFIX}{email}")

        user = await self.crud.get_by_email(email)
        if not user:
            raise SessionExpiredError()

        return await self.session_service.create_session(
            user.id,
            ip,
            user_agent
        )

    async def get_current_admin_user(self, session_id: str) -> AdminUser:
        data = await self.session_service.get_session(
            session_id
        )
        if not data:
            raise SessionExpiredError()

        user = await self.crud.get_by_id(data["user_id"])
        if not user:
            await self.session_service.invalidate_session(session_id)
            raise SessionExpiredError()

        if not user.is_active:
            await self.session_service.invalidate_session(session_id)
            raise AccountInactiveError()

        return user
