from pathlib import Path
from uuid import uuid4

from app.core.models import Conversation, Message
from app.storage.database import Database


def _database_path() -> Path:
    return Path.cwd() / f".test-storage-{uuid4().hex}.db"


def test_database_round_trips_conversations() -> None:
    path = _database_path()
    database = Database(path)
    try:
        conversation = Conversation(title="Saved chat")
        conversation.messages.append(Message(role="user", content="Remember this"))
        database.save_conversation(conversation)

        loaded = database.load_conversations()

        assert loaded[0].title == "Saved chat"
        assert loaded[0].messages[0].content == "Remember this"
    finally:
        database.close()
        path.unlink(missing_ok=True)


def test_database_persists_settings() -> None:
    path = _database_path()
    database = Database(path)
    try:
        database.save_settings({"provider": "mock", "model": "demo"})

        assert database.load_settings() == {"provider": "mock", "model": "demo"}
    finally:
        database.close()
        path.unlink(missing_ok=True)
