import chromadb

from config import (
    CHROMA_PATH,
    INITIAL_RETRIEVAL_K,
)

from retrieval.embeddings import EmbeddingModel


class DocumentSearch:

    def __init__(self):

        print("\nLoading document search engine...")

        self.embedding_model = EmbeddingModel()

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="knowledge"
            )
        )

        print("Document search engine ready.")

#search
    def search(
        self,
        question,
        user=None,
        top_k=None
    ):

        # Use the configured default if caller
        # does not provide a value.
        if top_k is None:
            top_k = INITIAL_RETRIEVAL_K

#create question
        embedding = self.embedding_model.encode(
            question
        )

#search for chromaDB
        try:

            results = self.collection.query(
                query_embeddings=[
                    embedding
                ],
                n_results=top_k,
            )

        except Exception as error:

            print(
                f"Document search error: {error}"
            )

            return []

#no results

        if not results.get("documents"):
            return []

        if not results["documents"][0]:
            return []

#extract results

        documents = results["documents"][0]

        metadatas = results["metadatas"][0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        output = []

        for index, document in enumerate(
            documents
        ):

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else float("inf")
            )

            output.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return output