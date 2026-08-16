"""Async database session management."""
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseSession:
    """Manages async database engine and session factory.
    
    Connection pool configuration rationale:
    - pool_size: Number of permanent connections. Set based on expected concurrency.
    - max_overflow: Extra connections allowed under load. Temporary, closed when idle.
    - pool_timeout: Max seconds to wait for a connection before raising error.
    - pool_recycle: Seconds before a connection is recycled (prevents stale connections).
    - pool_pre_ping: Test connections before use (handles dropped connections).
    
    WARNING: Total connections = instances * pool_size + max_overflow
    With 10 instances and pool_size=20, that's 200+ connections to PostgreSQL.
    PostgreSQL default max_connections is 100. Always calculate total load.
    """

    def __init__(
        self,
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
        pool_pre_ping: bool = True,
        echo: bool = False,
    ) -> None:
        self.engine = create_async_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        """Dispose engine and close all connections."""
        await self.engine.dispose()


async def get_db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
