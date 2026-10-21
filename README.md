# Enterprise Knowledge Intelligence Platform

A Python-based Retrieval-Augmented Generation (RAG) prototype for enterprise knowledge search and grounded question answering.

## Overview

This project demonstrates an end-to-end knowledge retrieval pipeline that ingests web content, processes documents into text chunks, generates embeddings, retrieves semantically relevant content, and builds context for LLM-based answer generation.

The current implementation uses public demonstration websites and is intended as a learning and portfolio project. It is not a production enterprise deployment.

## Key Features

- Web content ingestion using HTTP requests and HTML parsing
- Document validation and structured JSONL storage
- Content hashing for duplicate detection
- Text chunking with overlap
- Semantic embeddings using Sentence Transformers
- Cosine-similarity-based semantic search
- RAG context construction with source metadata
- Answer prompt construction with source citation instructions
- LLM-based answer generation
- Automated unit tests for core processing and retrieval components

## Architecture

```text
Public Web Sources
        |
        v
Document Ingestion
        |
        v
Document Validation and Storage
        |
        v
Text Chunking
        |
        v
Embedding Generation
        |
        v
Semantic Search
        |
        v
RAG Context Construction
        |
        v
LLM Answer Generation
        |
        v
Answer with Retrieved Sources
```

## Technology Stack

- Python
- httpx
- Beautiful Soup
- Pydantic
- Sentence Transformers
- PyTorch
- OpenAI Python SDK
- pytest
- JSONL-based local storage

## Project Structure

```text
enterprise-knowledge-ai/
├── app/
│   └── processing/
├── config/
├── data/
│   └── urls.txt
├── tests/
├── .gitignore
├── requirements.txt
└── README.md
```

Generated data, downloaded web pages, local virtual environments, test caches, and secret files should not be committed to the repository.

## Getting Started

### 1. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure the OpenAI API key

Set the `OPENAI_API_KEY` environment variable in your local PowerShell session. Do not hard-code API keys in source code or commit them to Git.

```powershell
$env:OPENAI_API_KEY = "YOUR_API_KEY"
```

Replace the placeholder locally with your own key. Never share the real key in screenshots, chat messages, or source control.

### 4. Run the question-answering demo

```powershell
python -m app.processing.answer_generator
```

Follow the terminal prompt to enter a question.

## Running Tests

Run the full test suite:

```powershell
python -m pytest -q -p no:cacheprovider --basetemp=.pytest-tmp\run
```

The current development environment has passed 80 tests. Test results may change as the project evolves.

## Current Limitations

- The current knowledge corpus uses public demonstration websites.
- Documents and embeddings are stored locally as JSONL files.
- Retrieval quality depends on the available documents and embedding model.
- Answer quality and citation grounding require further evaluation.
- Production deployment would require additional security, access control, observability, evaluation, and operational controls.

## Roadmap

- Add a repeatable ingestion workflow
- Improve retrieval evaluation and citation verification
- Add end-to-end integration tests
- Explore vector database integration
- Add a user interface for interactive knowledge search
- Strengthen security and access-control design

## Security

Never commit API keys, credentials, confidential documents, or internal company data. Use approved data sources and follow applicable organizational policies before connecting any enterprise systems.

## License

No license has been specified yet.
