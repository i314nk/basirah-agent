"""
Database connection and management for basīrah.
Uses PostgreSQL running in Docker.
"""

import os
import logging
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages PostgreSQL database connections using connection pooling.
    """

    def __init__(self):
        """Initialize database connection pool."""
        self.pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Create connection pool."""
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "basirah"),
                user=os.getenv("DB_USER", "basirah_user"),
                password=os.getenv("DB_PASSWORD", "basirah_secure_password_2025")
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Get database connection from pool.

        Usage:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM analyses")
        """
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """
        Get database cursor with automatic commit/rollback.

        Usage:
            with db.get_cursor() as cur:
                cur.execute("SELECT * FROM analyses")
                results = cur.fetchall()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()

    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        Execute SELECT query and return results.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of result dictionaries
        """
        with self.get_cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Execute INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of affected rows
        """
        with self.get_cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount

    def close(self):
        """Close all connections in pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")

    def health_check(self) -> bool:
        """
        Check if database is accessible.

        Returns:
            True if database is healthy, False otherwise
        """
        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Singleton instance
_db_manager: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Get database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


__all__ = ["DatabaseManager", "get_db"]
