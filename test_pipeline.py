import hashlib

from config import (
    DOCUMENT_FOLDER,
    SUPPORTED_EXTENSIONS,
)

from ingestion import (
    extract_file,
    chunk_extracted_sections,
)

from retrieval.search import DocumentSearch
from retrieval.reranker import rerank

from llm.qwen import Qwen

from security.permissions import (
    default_user,
    authorize_request,
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LOCAL DOCUMENT AI")
    print("=" * 70)

    # --------------------------------------------------------
    # CURRENT USER
    # --------------------------------------------------------

    user = default_user()

    print(
        "\nUser: "
        + str(user.get("username", "unknown"))
    )

    # --------------------------------------------------------
    # FIND SUPPORTED DOCUMENTS
    # --------------------------------------------------------

    files = [
        path
        for path in DOCUMENT_FOLDER.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        )
    ]

    if not files:

        print("\nNo supported documents found.")
        return

    print("\nDocuments found:")

    for file in files:
        print(
            " - "
            + str(file.relative_to(DOCUMENT_FOLDER))
        )

    # --------------------------------------------------------
    # LOAD SEARCH ENGINE
    # --------------------------------------------------------

    print("\nLoading document search...")

    search_engine = DocumentSearch()

    # --------------------------------------------------------
    # INDEX DOCUMENTS
    # --------------------------------------------------------

    for path in files:

        print(
            "\nProcessing: "
            + path.name
        )

        try:

            # ------------------------------------------------
            # EXTRACT CONTENT
            # ------------------------------------------------

            extracted = extract_file(path)

            if not extracted:

                print("  No readable content.")
                continue

            # ------------------------------------------------
            # CREATE CHUNKS
            # ------------------------------------------------

            chunks = chunk_extracted_sections(
                extracted
            )

            if not chunks:

                print("  No chunks created.")
                continue

            texts = [
                item["text"]
                for item in chunks
            ]

            # ------------------------------------------------
            # CREATE EMBEDDINGS
            # ------------------------------------------------

            print(
                "  Creating embeddings for "
                + str(len(texts))
                + " chunks..."
            )

            embeddings = (
                search_engine
                .embedding_model
                .encode_many(texts)
            )

            # ------------------------------------------------
            # FILE HASH
            # ------------------------------------------------

            file_hash = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()

            relative_path = str(
                path.relative_to(
                    DOCUMENT_FOLDER
                )
            )

            ids = []
            metadatas = []

            # ------------------------------------------------
            # METADATA
            # ------------------------------------------------

            for i, item in enumerate(chunks):

                ids.append(
                    file_hash + "_" + str(i)
                )

                metadata = {
                    "source": path.name,

                    "source_path": relative_path,

                    "file_type": path.suffix.lower(),

                    "page": (
                        item.get("page")
                        if item.get("page") is not None
                        else ""
                    ),

                    "location": (
                        item.get("location")
                        if item.get("location")
                        else ""
                    ),

                    "language": (
                        item.get("language")
                        if item.get("language")
                        else ""
                    ),

                    # Temporary development metadata.
                    "sensitivity": "public",

                    "department": "general",
                }

                metadatas.append(metadata)

            # ------------------------------------------------
            # DELETE OLD VERSION
            # ------------------------------------------------

            search_engine.collection.delete(
                where={
                    "source_path": relative_path
                }
            )

            # ------------------------------------------------
            # STORE IN CHROMADB
            # ------------------------------------------------

            search_engine.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

            print(
                "  Indexed "
                + str(len(chunks))
                + " chunks."
            )

        except Exception as error:

            print(
                "  ERROR processing "
                + path.name
                + ": "
                + str(error)
            )

    # --------------------------------------------------------
    # QUESTION LOOP
    # --------------------------------------------------------

    while True:

        print("\n" + "=" * 70)

        question = input(
            "Ask a question about your documents "
            "(type 'exit' to stop): "
        ).strip()

        if question.lower() == "exit":

            print("\nExiting.")
            break

        if not question:
            continue

        # ----------------------------------------------------
        # AI SECURITY GUARD
        # ----------------------------------------------------

        print(
            "\nChecking request permissions..."
        )

        security_result = authorize_request(
            user,
            question
        )

        allowed = security_result.get(
            "allowed",
            False
        )

        # ----------------------------------------------------
        # DENIED / UNCERTAIN
        # ----------------------------------------------------

        if not allowed:

            print("\n" + "=" * 70)
            print("ACCESS DENIED")
            print("=" * 70)

            category = security_result.get(
                "category",
                "unknown"
            )

            reason = security_result.get(
                "reason",
                "This request is not permitted."
            )

            print(
                "Category: "
                + str(category)
            )

            print(
                str(reason)
            )

            continue

        # ----------------------------------------------------
        # SEARCH DOCUMENTS
        # ----------------------------------------------------

        print(
            "\nSearching documents..."
        )

        candidates = search_engine.search(
            question,
            user=user
        )

        # ----------------------------------------------------
        # RERANK
        # ----------------------------------------------------

        results = rerank(
            candidates,
            top_k=3
        )

        print(
            "Found "
            + str(len(results))
            + " relevant chunks."
        )

        if not results:

            print(
                "\nI could not find relevant "
                "information in the documents."
            )

            continue

        # ----------------------------------------------------
        # ASK QWEN
        # ----------------------------------------------------

        qwen = Qwen()

        print(
            "\nSending information to Qwen..."
        )

        response = qwen.answer(
            question,
            results
        )

        # ----------------------------------------------------
        # ANSWER
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print("ANSWER")
        print("=" * 70)

        answer = response.get(
            "answer",
            "No answer was returned."
        )

        print(answer)

        # ----------------------------------------------------
        # THINKING MODE
        # ----------------------------------------------------

        if response.get(
            "thinking",
            False
        ):

            print(
                "\nMode: 🧠 Deep reasoning"
            )

        else:

            print(
                "\nMode: ⚡ Fast"
            )

        # ----------------------------------------------------
        # SOURCES
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print("SOURCES")
        print("=" * 70)

        sources = response.get(
            "sources",
            []
        )

        if sources:

            for source in sources:

                print(
                    "- "
                    + str(source)
                )

        else:

            for result in results:

                metadata = result.get(
                    "metadata",
                    {}
                )

                source = metadata.get(
                    "source",
                    "Unknown"
                )

                location = metadata.get(
                    "location",
                    ""
                )

                if location:

                    print(
                        "- "
                        + str(source)
                        + " ("
                        + str(location)
                        + ")"
                    )

                else:

                    print(
                        "- "
                        + str(source)
                    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()