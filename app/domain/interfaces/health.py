from typing import Protocol


class DatabaseHealthPort(Protocol):
    """Application-facing database health contract."""

    async def is_connected(self) -> bool:
        """Return whether a lightweight database connection succeeds."""

    async def has_schema(self) -> bool:
        """Return whether the foundation schema is reachable."""
