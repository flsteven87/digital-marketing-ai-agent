"""Direct PostgreSQL connection for OAuth users management."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, List, Optional
import psycopg
from psycopg.rows import dict_row
from urllib.parse import urlparse

from app.core.config import settings


class PostgresConnection:
    """Direct PostgreSQL connection manager."""
    
    def __init__(self):
        # Parse the DATABASE_URL
        url = urlparse(settings.DATABASE_URL)
        self.connection_params = {
            'host': url.hostname,
            'port': url.port,
            'dbname': url.path[1:],  # Remove leading slash
            'user': url.username,
            'password': url.password,
            'sslmode': 'require'
        }
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[psycopg.AsyncConnection, None]:
        """Get async PostgreSQL connection."""
        conn = await psycopg.AsyncConnection.connect(
            **self.connection_params,
            row_factory=dict_row
        )
        try:
            yield conn
        finally:
            await conn.close()
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results."""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return await cur.fetchall()
    
    async def execute_insert(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        """Execute INSERT query and return the inserted row."""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query + " RETURNING *", params)
                result = await cur.fetchone()
                await conn.commit()
                return result
    
    async def execute_update(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        """Execute UPDATE query and return the updated row."""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query + " RETURNING *", params)
                result = await cur.fetchone()
                await conn.commit()
                return result
    
    async def execute_delete(self, query: str, params: tuple = ()) -> bool:
        """Execute DELETE query and return success status."""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                affected_rows = cur.rowcount
                await conn.commit()
                return affected_rows > 0
    
    async def execute(self, query: str, params: tuple = ()) -> None:
        """Execute any SQL query without expecting results."""
        async with self.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                await conn.commit()


# Global instance
postgres_db = PostgresConnection()


async def get_postgres() -> PostgresConnection:
    """Get PostgreSQL connection instance."""
    return postgres_db