from app.exceptions.codes import ErrorCode
from app.exceptions.http import ConflictError, NotFoundError


class UserNotFoundError(NotFoundError):
    def __init__(self):
        super().__init__(
            code=ErrorCode.USER_NOT_FOUND,
            message="User not found",
        )


class UserAlreadyExistsError(ConflictError):
    def __init__(self):
        super().__init__(
            code=ErrorCode.CONFLICT,
            message="User with this email already exists",
        )
