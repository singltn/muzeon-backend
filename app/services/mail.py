import aiosmtplib
import logging
from email.message import EmailMessage

from app.core.config import settings
from app.exceptions.auth import SMTPError

logger = logging.getLogger("app.email")


class Email:
    def __init__(self):
        self.hostname = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.email_from = settings.SMTP_FROM
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.start_tls = settings.SMTP_TLS

    async def send_email(
            self,
            email_to: str,
            subject: str,
            content: str
    ) -> bool:
        message = EmailMessage()
        message["From"] = self.email_from
        message["To"] = email_to
        message["Subject"] = subject
        message.set_content(
            content
        )

        try:
            await aiosmtplib.send(
                message,
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=self.start_tls,
            )
            return True
        except Exception as e:
            logger.error(
                "smtp_send_failed",
                extra={
                    "event": "smtp_send_failed",
                    "to": email_to,
                    "subject": subject,
                    "error": str(e),
                },
            )
            raise SMTPError(str(e))

    async def send_otp_email(self, to_email: str, otp: str) -> bool:
        subject = "MUZEON вход в панель администратора"
        content = (
            f"Ваш код для входа в панель администратора: {otp}.\n"
            "Никому его не сообщайте. Код действует 5 минут."
        )
        return await self.send_email(to_email, subject, content)

    async def send_credentials_email(
        self,
        to_email: str,
        password: str,
        museum_name: str | None = None,
    ) -> bool:
        subject = "MUZEON — доступ к панели администратора"
        museum_line = (
            f"Музей: {museum_name}\n" if museum_name else ""
        )
        content = (
            "Вам создан аккаунт в панели администратора MUZEON.\n\n"
            f"{museum_line}"
            f"Email: {to_email}\n"
            f"Пароль: {password}\n\n"
            "При первом входе потребуется ввести пароль и одноразовый код из письма.\n"
            "Рекомендуем сменить пароль после входа."
        )
        return await self.send_email(to_email, subject, content)


mailer = Email()
