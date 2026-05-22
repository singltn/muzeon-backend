from sqlalchemy.orm import DeclarativeBase, declared_attr
from app.services.utils import to_snake_case

class Base(DeclarativeBase):

    @declared_attr.directive
    def __tablename__(cls):
        return to_snake_case(cls.__name__)