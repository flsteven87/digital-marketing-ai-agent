#!/usr/bin/env python3
"""Database migration script for AI Marketing Assistant.

This script creates the necessary tables for the chat and marketing system.
Run this script to set up the database schema.
"""

import os
import sys
from pathlib import Path
import psycopg
from urllib.parse import urlparse

# Add the app directory to the path
app_dir = Path(__file__).parent.parent
sys.path.append(str(app_dir))

from app.core.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    """Get PostgreSQL connection from DATABASE_URL."""
    try:
        # Parse the DATABASE_URL
        url = urlparse(settings.DATABASE_URL)
        
        # Create connection
        conn = psycopg.connect(
            host=url.hostname,
            port=url.port,
            dbname=url.path[1:],  # Remove leading slash
            user=url.username,
            password=url.password,
            sslmode='require'
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None


def create_marketing_tables():
    """Create marketing-related tables in the database."""
    logger.info("Starting database migration for marketing schema")
    
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        logger.info("Connected to PostgreSQL successfully")
        cursor = conn.cursor()
        
        # SQL statements to create tables
        sql_statements = [
            # Enable extensions
            """
            CREATE EXTENSION IF NOT EXISTS "pgcrypto";
            """,
            
            # Users table (extends auth.users)
            """
            CREATE TABLE IF NOT EXISTS public.users (
                id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                company TEXT,
                role TEXT DEFAULT 'user',
                avatar_url TEXT,
                phone TEXT,
                timezone TEXT DEFAULT 'Asia/Taipei',
                language TEXT DEFAULT 'zh-TW',
                is_active BOOLEAN DEFAULT true,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Chat sessions
            """
            CREATE TABLE IF NOT EXISTS public.chat_sessions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL,
                brand_id UUID,
                title TEXT,
                context JSONB DEFAULT '{}',
                is_archived BOOLEAN DEFAULT false,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Chat messages
            """
            CREATE TABLE IF NOT EXISTS public.chat_messages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                session_id UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Organizations
            """
            CREATE TABLE IF NOT EXISTS public.organizations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                owner_id UUID NOT NULL,
                logo_url TEXT,
                website TEXT,
                industry TEXT,
                description TEXT,
                settings JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Brands
            """
            CREATE TABLE IF NOT EXISTS public.brands (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                description TEXT,
                logo_url TEXT,
                website TEXT,
                industry TEXT,
                target_audience TEXT,
                brand_voice TEXT,
                brand_values TEXT[],
                color_palette JSONB DEFAULT '{}',
                social_profiles JSONB DEFAULT '{}',
                settings JSONB DEFAULT '{}',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Generated content
            """
            CREATE TABLE IF NOT EXISTS public.generated_content (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL,
                brand_id UUID REFERENCES public.brands(id) ON DELETE SET NULL,
                session_id UUID REFERENCES public.chat_sessions(id) ON DELETE SET NULL,
                content_type TEXT NOT NULL,
                platform TEXT[],
                title TEXT,
                content TEXT NOT NULL,
                media_urls TEXT[],
                hashtags TEXT[],
                metadata JSONB DEFAULT '{}',
                status TEXT DEFAULT 'draft',
                scheduled_at TIMESTAMPTZ,
                published_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
        ]
        
        # Index creation statements
        index_statements = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);",
            "CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON public.chat_sessions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON public.chat_messages(session_id);",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON public.chat_messages(created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_organizations_slug ON public.organizations(slug);",
            "CREATE INDEX IF NOT EXISTS idx_brands_organization ON public.brands(organization_id);",
            "CREATE INDEX IF NOT EXISTS idx_generated_content_user ON public.generated_content(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_generated_content_brand ON public.generated_content(brand_id);",
        ]
        
        # RLS statements
        rls_statements = [
            "ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE public.brands ENABLE ROW LEVEL SECURITY;",
            "ALTER TABLE public.generated_content ENABLE ROW LEVEL SECURITY;",
        ]
        
        # RLS policies
        policy_statements = [
            """
            DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
            CREATE POLICY "Users can view own profile" ON public.users
                FOR SELECT USING (auth.uid() = id);
            """,
            """
            DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
            CREATE POLICY "Users can update own profile" ON public.users
                FOR UPDATE USING (auth.uid() = id);
            """,
            """
            DROP POLICY IF EXISTS "Users can manage own chat sessions" ON public.chat_sessions;
            CREATE POLICY "Users can manage own chat sessions" ON public.chat_sessions
                FOR ALL USING (user_id = auth.uid());
            """,
            """
            DROP POLICY IF EXISTS "Users can manage own chat messages" ON public.chat_messages;
            CREATE POLICY "Users can manage own chat messages" ON public.chat_messages
                FOR ALL USING (
                    EXISTS (
                        SELECT 1 FROM public.chat_sessions
                        WHERE id = chat_messages.session_id
                        AND user_id = auth.uid()
                    )
                );
            """,
        ]
        
        # Trigger function for updated_at
        trigger_statements = [
            """
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            """,
            """
            DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
            CREATE TRIGGER update_users_updated_at 
                BEFORE UPDATE ON public.users
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            DROP TRIGGER IF EXISTS update_chat_sessions_updated_at ON public.chat_sessions;
            CREATE TRIGGER update_chat_sessions_updated_at 
                BEFORE UPDATE ON public.chat_sessions
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            DROP TRIGGER IF EXISTS update_organizations_updated_at ON public.organizations;
            CREATE TRIGGER update_organizations_updated_at 
                BEFORE UPDATE ON public.organizations
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            DROP TRIGGER IF EXISTS update_brands_updated_at ON public.brands;
            CREATE TRIGGER update_brands_updated_at 
                BEFORE UPDATE ON public.brands
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            DROP TRIGGER IF EXISTS update_generated_content_updated_at ON public.generated_content;
            CREATE TRIGGER update_generated_content_updated_at 
                BEFORE UPDATE ON public.generated_content
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
        ]
        
        # Execute all statements
        all_statements = (
            [("Extension", stmt) for stmt in sql_statements[:1]] +
            [("Table", stmt) for stmt in sql_statements[1:]] +
            [("Index", stmt) for stmt in index_statements] +
            [("RLS", stmt) for stmt in rls_statements] +
            [("Policy", stmt) for stmt in policy_statements] +
            [("Trigger", stmt) for stmt in trigger_statements]
        )
        
        success_count = 0
        for category, statement in all_statements:
            try:
                # Execute SQL statement
                cursor.execute(statement.strip())
                conn.commit()
                logger.info(f"✅ {category} executed successfully")
                success_count += 1
            except Exception as e:
                # Some statements might fail if they already exist, which is OK
                if "already exists" in str(e) or "does not exist" in str(e):
                    logger.info(f"⚠️  {category}: {str(e)[:100]}... (expected)")
                    conn.rollback()
                else:
                    logger.warning(f"⚠️  {category} failed: {str(e)[:100]}...")
                    conn.rollback()
        
        cursor.close()
        conn.close()
        logger.info(f"Migration completed. {success_count}/{len(all_statements)} statements executed.")
        return True
        
    except Exception as e:
        logger.error(f"Database migration failed: {str(e)}")
        return False


def check_migration_status():
    """Check the current status of the migration."""
    logger.info("Checking migration status")
    
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        tables_to_check = [
            "users", "chat_sessions", "chat_messages", 
            "organizations", "brands", "generated_content"
        ]
        
        tables_info = []
        
        for table_name in tables_to_check:
            try:
                # Check if table exists and get row count
                cursor.execute(f"SELECT COUNT(*) FROM public.{table_name}")
                row_count = cursor.fetchone()[0]
                tables_info.append(f"✅ {table_name}: {row_count} rows")
            except Exception:
                tables_info.append(f"❌ {table_name}: NOT FOUND")
        
        cursor.close()
        conn.close()
        
        logger.info("Migration status check completed")
        print("\\n📊 Marketing Assistant Schema Status:")
        print("=" * 40)
        for info in tables_info:
            print(info)
        print("=" * 40)
        
        return True
        
    except Exception as e:
        logger.error(f"Migration status check failed: {str(e)}")
        return False


def drop_marketing_tables():
    """Drop marketing-related tables (use with caution!)."""
    logger.warning("⚠️  Starting to drop marketing tables - THIS WILL DELETE ALL DATA!")
    
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Drop tables in reverse dependency order
        drop_statements = [
            "DROP TABLE IF EXISTS public.generated_content CASCADE;",
            "DROP TABLE IF EXISTS public.brands CASCADE;",
            "DROP TABLE IF EXISTS public.organizations CASCADE;",
            "DROP TABLE IF EXISTS public.chat_messages CASCADE;",
            "DROP TABLE IF EXISTS public.chat_sessions CASCADE;",
            "DROP TABLE IF EXISTS public.users CASCADE;",
            "DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;",
        ]
        
        for statement in drop_statements:
            try:
                logger.info(f"Executing: {statement}")
                cursor.execute(statement)
                conn.commit()
            except Exception as e:
                logger.warning(f"Drop statement failed: {str(e)[:100]}...")
                conn.rollback()
        
        cursor.close()
        conn.close()
        logger.info("Successfully dropped all marketing tables")
        return True
        
    except Exception as e:
        logger.error(f"Failed to drop marketing tables: {str(e)}")
        return False


def main():
    """Main migration function with command line interface."""
    if len(sys.argv) < 2:
        print("🗃️  AI Marketing Assistant Migration Tool")
        print("=" * 40)
        print("Usage:")
        print("  python migrate_database.py create   # Create tables")
        print("  python migrate_database.py drop     # Drop tables (⚠️  DANGER)")
        print("  python migrate_database.py status   # Check status")
        print("  python migrate_database.py reset    # Drop and recreate")
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        print("🏗️  Creating marketing tables...")
        if create_marketing_tables():
            check_migration_status()
        
    elif command == "drop":
        confirm = input("⚠️  Are you sure you want to DROP ALL marketing tables? Type 'DELETE' to confirm: ")
        if confirm == "DELETE":
            if drop_marketing_tables():
                print("🗑️  All marketing tables have been dropped.")
        else:
            print("❌ Operation cancelled.")
    
    elif command == "status":
        check_migration_status()
        
    elif command == "reset":
        confirm = input("⚠️  Are you sure you want to RESET ALL marketing tables? Type 'RESET' to confirm: ")
        if confirm == "RESET":
            print("🗑️  Dropping existing tables...")
            if drop_marketing_tables():
                print("🏗️  Creating new tables...")
                if create_marketing_tables():
                    check_migration_status()
                    print("✅ Database reset completed!")
        else:
            print("❌ Operation cancelled.")
            
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: create, drop, status, reset")


if __name__ == "__main__":
    main()