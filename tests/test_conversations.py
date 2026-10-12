from pathlib import Path
from uuid import uuid4

from app.core.application import BoltApplication
from app.core.models import Message


def _database_path() -> Path:
    return Path.cwd() / f".test-conversations-{uuid4().hex}.db"


def test_new_conversation_becomes_active() -> None:
    path = _database_path()
    application = BoltApplication(database_path=path)
    try:
        first = application.active_conversation
        second = application.create_conversation("Planning")

        assert application.active_conversation is second
        assert application.conversations == [second, first]
    finally:
        application.close()
        path.unlink(missing_ok=True)


def test_messages_are_kept_in_order() -> None:
    path = _database_path()
    application = BoltApplication(database_path=path)
    try:
        conversation = application.active_conversation
        conversation.messages.extend(
            [Message(role="user", content="Hi"), Message(role="assistant", content="Hello")]
        )

        assert [message.role for message in conversation.messages] == ["user", "assistant"]
    finally:
        application.close()
        path.unlink(missing_ok=True)

