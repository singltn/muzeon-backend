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

class AccountInactiveError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code=ErrorCode.INVALID_OTP,
            message="Account is inactive"
        )

class TerminateCurrentSessionError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.TERMINATE_CURRENT_SESSION,
            message="You can not terminate current session"
        )