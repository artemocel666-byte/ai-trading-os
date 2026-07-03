from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class SqlAlchemyDatabaseHealth:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def is_connected(self) -> bool:
        try:
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception:
            return False
        return True

    async def has_schema(self) -> bool:
        try:
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT key FROM system_state LIMIT 1"))
        except Exception:
            return False
        return True
