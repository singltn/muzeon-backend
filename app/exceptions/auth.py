from fastapi import status
from app.exceptions.base import AppException
from app.exceptions.codes import ErrorCode


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.INVALID_CREDENTIALS,
            message="Invalid credentials",
        )


class InvalidOTPError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.INVALID_OTP,
            message="Invalid OTP code",
        )


class SMTPError(AppException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.SMTP_ERROR,
            message=message,
        )


class AccountInactiveError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code=ErrorCode.ACCOUNT_INACTIVE,
            message="Account is inactive"
        )


class SessionExpiredError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.SESSION_EXPIRED,
            message="Account is inactive"
        )


class AuthenticationRequiredError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.AUTH_REQUIRED,
            message="Authentication required",
        )


class TooManyAuthRequests(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code=ErrorCode.AUTH_TOO_MANY_REQUESTS,
            message="Too many requests. Please, try again after 5 minutes",
        )
