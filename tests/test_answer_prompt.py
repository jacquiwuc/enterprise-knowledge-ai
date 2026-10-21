
import pytest

from app.processing.answer_prompt import (
    SYSTEM_PROMPT,
    build_answer_messages,
)


def test_build_answer_messages_returns_system_and_user_messages():
    messages = build_answer_messages(
        "What does the document say?",
        "[Source 1] Content: Example policy",
    )

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_prompt_contains_question_and_context():
    messages = build_answer_messages(
        "What is the policy?",
        "[Source 1] Content: Approval is required.",
    )

    assert "What is the policy?" in messages[1]["content"]
    assert "Approval is required." in messages[1]["content"]


def test_system_prompt_requires_evidence_and_citations():
    assert "Do not invent facts" in SYSTEM_PROMPT
    assert "source" in SYSTEM_PROMPT.lower()
    assert "not enough evidence" in SYSTEM_PROMPT


def test_build_answer_messages_rejects_blank_question():
    with pytest.raises(ValueError, match="Question must not be empty"):
        build_answer_messages("   ", "Some context")


def test_build_answer_messages_rejects_blank_context():
    with pytest.raises(ValueError, match="Context must not be empty"):
        build_answer_messages("Some question", "   ")
