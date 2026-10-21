
import os
from typing import Any

from openai import OpenAI

from app.processing.answer_prompt import build_answer_messages
from app.processing.rag_pipeline import retrieve_context


DEFAULT_MODEL = "gpt-4.1-mini"


class AnswerGenerator:
    """Generate evidence-grounded answers from retrieved context."""

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        """Generate an answer using the supplied retrieved context."""
        messages = build_answer_messages(question, context)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
        )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError("The model returned an empty answer")

        return answer.strip()


def answer_question(
    question: str,
    top_k: int = 3,
    max_context_chars: int = 6000,
) -> dict[str, Any]:
    """Retrieve relevant knowledge and generate a grounded answer."""
    retrieved = retrieve_context(
        question,
        top_k=top_k,
        max_context_chars=max_context_chars,
    )

    if not retrieved["context"].strip():
        return {
            "question": question,
            "answer": (
                "I could not find relevant information in the available "
                "knowledge sources, so I cannot provide a reliable answer."
            ),
            "sources": [],
            "result_count": 0,
        }

    generator = AnswerGenerator()
    answer = generator.generate_answer(
        question,
        retrieved["context"],
    )

    return {
        "question": retrieved["question"],
        "answer": answer,
        "sources": retrieved["sources"],
        "result_count": retrieved["result_count"],
    }


if __name__ == "__main__":
    question = input("Ask a knowledge question: ").strip()

    try:
        result = answer_question(question)

        print("\n=== Answer ===")
        print(result["answer"])

        print("\n=== Retrieved Sources ===")
        for source in result["sources"]:
            print(
                f"- {source['title']} | "
                f"{source['source_url']} | "
                f"score={source['score']:.4f}"
            )

    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        print(f"Unable to answer question: {exc}")
