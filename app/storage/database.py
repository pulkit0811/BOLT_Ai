from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.core.models import Conversation, Message


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        with self.connection:
            self.connection.executescript(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def load_conversations(self) -> list[Conversation]:
        rows = self.connection.execute(
            "SELECT id, title, created_at FROM conversations ORDER BY updated_at DESC"
        ).fetchall()
        conversations: list[Conversation] = []
        for row in rows:
            messages = self.connection.execute(
                "SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id",
                (row["id"],),
            ).fetchall()
            conversations.append(
                Conversation(
                    id=row["id"],
                    title=row["title"],
                    created_at=_parse_datetime(row["created_at"]),
                    messages=[
                        Message(
                            role=message["role"],
                            content=message["content"],
                            created_at=_parse_datetime(message["created_at"]),
                        )
                        for message in messages
                    ],
                )
            )
        return conversations

    def save_conversation(self, conversation: Conversation) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO conversations(id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET title = excluded.title, updated_at = excluded.updated_at
                """,
                (
                    conversation.id,
                    conversation.title,
                    conversation.created_at.isoformat(),
                    conversation.updated_at.isoformat(),
                ),
            )
            self.connection.execute(
                "DELETE FROM messages WHERE conversation_id = ?", (conversation.id,)
            )
            self.connection.executemany(
                "INSERT INTO messages(conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                [
                    (conversation.id, message.role, message.content, message.created_at.isoformat())
                    for message in conversation.messages
                ],
            )

    def delete_conversation(self, conversation_id: str) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

    def load_settings(self) -> dict[str, str]:
        rows = self.connection.execute("SELECT key, value FROM settings").fetchall()
        return {row["key"]: row["value"] for row in rows}

    def save_settings(self, values: dict[str, str]) -> None:
        with self.connection:
            self.connection.executemany(
                "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                values.items(),
            )

    def close(self) -> None:
        self.connection.close()


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed
