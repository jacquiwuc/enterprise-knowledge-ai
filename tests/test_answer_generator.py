
import pytest

from app.processing import answer_generator


def test_generator_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        answer_generator.AnswerGenerator()


def test_generate_answer_returns_model_response(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class FakeMessage:
        content = "The document says approval is required. [Source 1]"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["model"] == "gpt-4.1-mini"
            assert kwargs["temperature"] == 0
            assert len(kwargs["messages"]) == 2
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

        def __init__(self, api_key):
            assert api_key == "test-key"

    monkeypatch.setattr(
        answer_generator,
        "OpenAI",
        FakeClient,
    )

    generator = answer_generator.AnswerGenerator()
    result = generator.generate_answer(
        "What does the document say?",
        "[Source 1] Content: Approval is required.",
    )

    assert result == "The document says approval is required. [Source 1]"


def test_generate_answer_rejects_empty_context(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class FakeClient:
        def __init__(self, api_key):
            pass

    monkeypatch.setattr(
        answer_generator,
        "OpenAI",
        FakeClient,
    )

    generator = answer_generator.AnswerGenerator()

    with pytest.raises(ValueError, match="Context must not be empty"):
        generator.generate_answer("Question?", "   ")


def test_answer_question_returns_fallback_without_context(monkeypatch):
    monkeypatch.setattr(
        answer_generator,
        "retrieve_context",
        lambda *args, **kwargs: {
            "question": "Unknown question",
            "context": "",
            "sources": [],
            "result_count": 0,
        },
    )

    result = answer_generator.answer_question("Unknown question")

    assert result["result_count"] == 0
    assert result["sources"] == []
    assert "cannot provide a reliable answer" in result["answer"]
