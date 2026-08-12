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

from src.rag.embedding_generator import (
    EmbeddingGenerator
)

from src.rag.vector_store import (
    VectorStore
)

from src.rag.retriever import (
    Retriever
)

from src.rag.document_processor import (
    convert_dataframe_to_chunks
)

from app.utils.data_manager import DataManager


def test_rag_retrieval():
    df = DataLoader.load_data("data/raw/sales_data.csv")

    # Use the proper document processor to create chunks
    documents = convert_dataframe_to_chunks(
        df.head(100),  # Limit for faster testing
        dataset_name="test_dataset",
        rows_per_chunk=10
    )

    embedding_generator = EmbeddingGenerator()

    # Extract text for embeddings
    document_texts = [doc["text"] for doc in documents]
    embeddings = embedding_generator.generate_embeddings(document_texts)

    dataset_fingerprint = DataManager.generate_dataset_fingerprint(df)
    vector_store = VectorStore(dataset_fingerprint)

    vector_store.create_index(embeddings, documents)

    retriever = Retriever(embedding_generator, vector_store)

    results = retriever.retrieve("highest profit technology sales")

    # Check that we get results
    assert isinstance(results, list)
    # Check that each result is a dict with text and metadata (as stored in vector_store)
    for result in results:
        assert isinstance(result, dict)
        assert "text" in result
        assert "metadata" in result