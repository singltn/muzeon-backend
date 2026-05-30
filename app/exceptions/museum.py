from app.exceptions.codes import ErrorCode
from app.exceptions.http import ConflictError, NotFoundError


class MuseumAlreadyExistsError(ConflictError):
    def __init__(self):
        super().__init__(
            code=ErrorCode.CONFLICT,
            message="Museum already exists",
        )


class MuseumNotFoundError(NotFoundError):
    def __init__(self):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message="Museum not found",
        )
