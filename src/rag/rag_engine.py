from app.utils.data_manager import DataManager

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


class RAGEngine:

    def __init__(self, df):

        self.df = df

        self.embedding_generator = (
            EmbeddingGenerator()
        )

        dataset_fingerprint = (
            DataManager.get_dataset_fingerprint()
        )

        if not dataset_fingerprint:

            dataset_fingerprint = (
                DataManager.generate_dataset_fingerprint(
                    df
                )
            )

        self.vector_store = (
            VectorStore(
                dataset_fingerprint
            )
        )

        self.retriever = None

        loaded = (
            self.vector_store.load_index()
        )

        if loaded:

            print(
                f"Loaded FAISS index for dataset: "
                f"{dataset_fingerprint[:12]}"
            )

            self.retriever = Retriever(
                self.embedding_generator,
                self.vector_store
            )

        else:

            print(
                "No existing FAISS index found."
            )

            self.build_index()

    def build_index(self):

        print(
            "Building enhanced dataset documents..."
        )

        # Use the improved document processor for better chunking
        documents = convert_dataframe_to_chunks(
            self.df.head(min(len(self.df), 5000)),  # Limit to 5000 rows for performance
            dataset_name="dataset",
            rows_per_chunk=10
        )

        # Extract just the text content for embedding
        document_texts = [doc["text"] for doc in documents]

        print(
            f"Generated {len(document_texts)} documents"
        )

        print(
            "Generating embeddings..."
        )

        embeddings = (
            self.embedding_generator
            .generate_embeddings(
                document_texts
            )
        )

        print(
            "Embeddings generated"
        )

        self.vector_store.create_index(
            embeddings,
            documents  # Store the full document objects with metadata
        )

        print(
            "Saving dataset-specific FAISS index..."
        )

        self.vector_store.save_index()

        self.retriever = Retriever(
            self.embedding_generator,
            self.vector_store
        )

        print(
            "Dataset index ready"
        )

    def retrieve(
        self,
        question
    ):

        if self.retriever is None:

            return []

        return self.retriever.retrieve(
            question,
            top_k=25
        )