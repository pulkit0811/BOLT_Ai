from __future__ import annotations

import json
from collections.abc import Mapping
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from app.core.application import BoltApplication
from app.core.models import Conversation, Message


class BoltRequestHandler(BaseHTTPRequestHandler):
    application: BoltApplication

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        parts = path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "api" and parts[1] == "conversations":
            self._respond(404, {"error": "Conversation id is required"})
            return
        if len(parts) == 3 and parts[:2] == ["api", "conversations"]:
            conversation = self._find_conversation(parts[2])
            if conversation is None:
                self._respond(404, {"error": "Conversation not found"})
                return
            self.application.delete_conversation(conversation)
            self._respond(200, {"ok": True})
            return
        self._respond(404, {"error": "Route not found"})

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/state":
            self._respond(200, self._state())
            return
        self._respond(404, {"error": "Route not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/conversations":
            conversation = self.application.create_conversation()
            self._respond(201, self._conversation(conversation))
            return
        if path == "/api/active":
            payload = self._read_json()
            conversation_id = str(payload.get("conversation_id", "")) if isinstance(payload, Mapping) else ""
            conversation = self._find_conversation(conversation_id)
            if conversation is None:
                self._respond(404, {"error": "Conversation not found"})
                return
            self.application.active_conversation = conversation
            self._respond(200, self._conversation(conversation))
            return
        if path == "/api/voice-input":
            payload = self._read_json()
            content = str(payload.get("content", "")).strip() if isinstance(payload, Mapping) else ""
            if not content:
                self._respond(400, {"error": "Voice input is required"})
                return
            self._respond(200, self._answer(self.application.active_conversation, content))
            return
        parts = path.strip("/").split("/")
        if len(parts) == 4 and parts[:2] == ["api", "conversations"] and parts[3] == "messages":
            conversation = self._find_conversation(parts[2])
            payload = self._read_json()
            content = str(payload.get("content", "")).strip() if isinstance(payload, Mapping) else ""
            if conversation is None:
                self._respond(404, {"error": "Conversation not found"})
                return
            if not content:
                self._respond(400, {"error": "Message content is required"})
                return
            self._respond(200, self._answer(conversation, content))
            return
        self._respond(404, {"error": "Route not found"})

    def log_message(self, format: str, *args: object) -> None:
        return

    def _find_conversation(self, conversation_id: str) -> Conversation | None:
        return next((item for item in self.application.conversations if item.id == conversation_id), None)

    def _read_json(self) -> object:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            return {}

    def _answer(self, conversation: Conversation, content: str) -> dict[str, object]:
        self.application.active_conversation = conversation
        if not conversation.messages:
            conversation.title = content[:42] + ("..." if len(content) > 42 else "")
        conversation.messages.append(Message(role="user", content=content))
        response = self.application.provider.complete(conversation.messages)
        assistant_message = Message(role="assistant", content=response)
        conversation.messages.append(assistant_message)
        self.application.save_conversation(conversation)
        return {"message": self._message(assistant_message), "conversation": self._conversation(conversation)}

    def _state(self) -> dict[str, object]:
        config = self.application.config
        is_cloud = config.provider == "ollama" and (config.endpoint.lower().startswith("https://") or ":cloud" in config.model)
        return {
            "conversations": [self._conversation(item) for item in self.application.conversations],
            "activeId": self.application.active_conversation.id,
            "engine": {
                "provider": config.provider,
                "model": config.model,
                "status": "demo" if config.provider == "mock" else "online",
                "isCloud": is_cloud,
            },
        }

    def _conversation(self, conversation: Conversation) -> dict[str, object]:
        return {
            "id": conversation.id,
            "title": conversation.title,
            "messages": [self._message(message) for message in conversation.messages],
        }

    def _message(self, message: Message) -> dict[str, str]:
        return {"role": message.role, "content": message.content}

    def _respond(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)


def create_server(application: BoltApplication, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    handler = type("ConfiguredBoltRequestHandler", (BoltRequestHandler,), {"application": application})
    return ThreadingHTTPServer((host, port), handler)


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    application = BoltApplication()
    server = create_server(application, host, port)
    try:
        print(f"Bolt API listening on http://{host}:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        application.close()


if __name__ == "__main__":
    serve()
