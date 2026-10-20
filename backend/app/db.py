"""Modul koneksi dan pooling database PostgreSQL + pgvector (docs/sdd.md)."""

from contextlib import contextmanager
from typing import Generator, Optional
from pgvector.psycopg import register_vector
import psycopg
from psycopg_pool import ConnectionPool

from backend.app.config import settings

# Pool koneksi global untuk dipakai ulang antar request
_pool: Optional[ConnectionPool] = None


def init_db_pool() -> ConnectionPool:
    """Inisialisasi pool koneksi dan daftarkan ekstensi pgvector."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=10,
            configure=lambda conn: register_vector(conn),
        )
    return _pool


def close_db_pool() -> None:
    """Tutup seluruh koneksi di dalam pool saat aplikasi berhenti."""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


@contextmanager
def get_db_connection() -> Generator[psycopg.Connection, None, None]:
    """Pinjam satu koneksi dari pool lalu kembalikan otomatis setelah selesai."""
    pool = init_db_pool()
    with pool.connection() as conn:
        yield conn
