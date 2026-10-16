
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "chat_history.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
            )
        """)


def create_conversation(title="New conversation"):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,),
        )
        return cursor.lastrowid


def save_message(conversation_id, role, content):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content),
        )


def get_conversations():
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            ORDER BY id DESC
            """
        ).fetchall()


def get_messages(conversation_id):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (conversation_id,),
        ).fetchall()
