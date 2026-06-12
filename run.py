import uvicorn

from alembic import command
from alembic.config import Config
from app.main import app
from app.core.config import settings


if __name__ == '__main__':
    alembic_config = Config('alembic.ini')
    command.upgrade(alembic_config, 'head')
    uvicorn.run(
        'run:app',
        host='0.0.0.0',
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.RELOAD,
    )