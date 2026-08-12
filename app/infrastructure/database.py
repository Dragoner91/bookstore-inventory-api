from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.infrastructure.tables import BookTable
from app.config import settings

# pool_pre_ping descarta conexiones muertas: Render duerme el servicio y al
# despertar las del pool ya no sirven
engine = create_async_engine(settings.database_url, pool_pre_ping=True)

# expire_on_commit=False para poder leer el objeto despues del commit sin que
# SQLAlchemy dispare un refresh implicito, que en async no se resuelve solo
session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(BookTable.metadata.create_all)
