from fastapi import status
from app.exceptions.base import AppException
from app.exceptions.codes import ErrorCode


class NotFoundError(AppException):
    def __init__(self, code: str, message: str = "Not Found"):
        super().__init__(status.HTTP_404_NOT_FOUND, code, message)


class ConflictError(AppException):
    def __init__(self, code: str, message: str = "Conflict"):
        super().__init__(status.HTTP_409_CONFLICT, code, message)


class BadRequestError(AppException):
    def __init__(self, code: str, message: str = "Bad Request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, code, message)

class PermissionDeniedError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code=ErrorCode.PERMISSION_DENIED,
            message="Permission denied",
        )