from app.ai.mock_provider import MockProvider
from app.ai.ollama_provider import OllamaProvider
from app.core.models import Message


def test_mock_provider_is_explicitly_local() -> None:
    response = MockProvider().complete([Message(role="user", content="What is Python?")])

    assert "local demo response" in response
    assert "What is Python?" in response


def test_ollama_provider_uses_configured_endpoint() -> None:
    provider = OllamaProvider(
        model="deepseek-v4.1-flash",
        endpoint="https://ollama.com/v1",
        api_key="test-key",
    )

    assert provider.model == "deepseek-v4.1-flash"

