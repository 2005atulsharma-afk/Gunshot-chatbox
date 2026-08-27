from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


class EmbeddingModel:

    def __init__(self):

        print(
            f"Loading embedding model: "
            f"{EMBEDDING_MODEL}"
        )

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        print("Embedding model ready.")

    def encode(self, text):

        return self.model.encode(
            text,
            normalize_embeddings=True
        ).tolist()

    def encode_many(self, texts):

        return self.model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()