import sqlite3
from pathlib import Path

DB_PATH = Path("nexus.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry REAL NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                status TEXT NOT NULL DEFAULT 'OPEN',
                exit_price REAL,
                result REAL,
                note TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                closed_at TEXT
            )
        """)
        conn.commit()


def get_open_trades():
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM trades WHERE status = 'OPEN' ORDER BY id DESC"
        ).fetchall()


def get_trade_count():
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
