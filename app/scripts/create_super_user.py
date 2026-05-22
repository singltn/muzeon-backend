import asyncio
import getpass

from app.db.session import async_session
from app.db.models import AdminUser
from app.core.security import hash_password
from app.enums import UserRoleEnum
from sqlalchemy import select

async def main():

    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")

    async with async_session() as session:
        existing = await session.scalar(
            select(AdminUser).where(
                AdminUser.email == email
            )
        )

        if existing:
            print("\nСупер-админ с указанной почтой уже зарегистрирован!")
            return

        user = AdminUser(
            email=email,
            password=hash_password(password),
            first_name=email,
            last_name=email,
            role=UserRoleEnum.super_admin,
            is_active=True,
        )

        session.add(user)
        await session.commit()

    print("\nСупер-пользователь успешно зарегистрирован!")




if __name__ == "__main__":
    asyncio.run(main())