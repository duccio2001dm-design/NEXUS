import sqlite3
from pathlib import Path
from datetime import datetime, timezone

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


def create_trade(symbol, side, entry, stop_loss=None, take_profit=None):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO trades
            (symbol, side, entry, stop_loss, take_profit)
            VALUES (?, ?, ?, ?, ?)
            """,
            (symbol, side, entry, stop_loss, take_profit),
        )
        conn.commit()
        return cursor.lastrowid


def close_trade(trade_id, exit_price):
    with get_connection() as conn:
        trade = conn.execute(
            "SELECT * FROM trades WHERE id = ? AND status = 'OPEN'",
            (trade_id,),
        ).fetchone()

        if trade is None:
            return None

        if trade["side"] == "LONG":
            result = exit_price - trade["entry"]
        else:
            result = trade["entry"] - exit_price

        conn.execute(
            """
            UPDATE trades
            SET status = 'CLOSED',
                exit_price = ?,
                result = ?,
                closed_at = ?
            WHERE id = ?
            """,
            (
                exit_price,
                result,
                datetime.now(timezone.utc).isoformat(),
                trade_id,
            ),
        )
        conn.commit()
        return result
