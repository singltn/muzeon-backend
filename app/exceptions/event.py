from app.exceptions.codes import ErrorCode
from app.exceptions.http import BadRequestError, NotFoundError


class EventNotFoundError(NotFoundError):
    def __init__(self):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message="Event not found",
        )


class EventLocationNotFoundError(NotFoundError):
    def __init__(self):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message="Event location not found",
        )


class EventTypeNotFoundError(NotFoundError):
    def __init__(self):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message="Event type not found",
        )


class InvalidEventStatusTransitionError(BadRequestError):
    def __init__(self, message: str = "Invalid event status transition"):
        super().__init__(
            code=ErrorCode.BAD_REQUEST,
            message=message,
        )
