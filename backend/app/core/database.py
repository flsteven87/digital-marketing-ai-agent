from typing import AsyncGenerator
from supabase import create_client, Client
from supabase.client import ClientOptions
import httpx

from app.core.config import settings


class SupabaseClient:
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            options = ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
            )
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY,
                options=options
            )
        return cls._instance


def get_supabase() -> Client:
    return SupabaseClient.get_client()


async def get_async_supabase() -> AsyncGenerator[Client, None]:
    client = get_supabase()
    try:
        yield client
    finally:
        pass