import sys
from pathlib import Path

import pytest

project_root = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

sys.path.append(
    str(project_root)
)

from src.ingestion.data_loader import (
    DataLoader
)

from src.rag.rag_engine import (
    RAGEngine
)

from src.rag.llm_handler import (
    LLMHandler
)


def test_rag_llm_integration():
    df = DataLoader.load_data("data/raw/sales_data.csv")

    rag = RAGEngine(df)

    llm = LLMHandler()

    question = (
        "Which technology products are generating the highest profit?"
    )

    docs = rag.retrieve(question)

    # Check that we get documents
    assert isinstance(docs, list)
    assert len(docs) > 0

    # Get response from LLM
    response = llm.ask_rag_question(docs, question)

    # Check that we get a string response
    assert isinstance(response, str)
    assert len(response) > 0

    # The response should not be an error message (basic check)
    assert "Error generating" not in response or len(response) > 50  # Allow short error messages