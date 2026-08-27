import hashlib
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config import (
    DOCUMENT_FOLDER,
    SUPPORTED_EXTENSIONS,
)

from ingestion import (
    extract_file,
    chunk_extracted_sections,
)

from retrieval.search import DocumentSearch


# ============================================================
# DOCUMENT INDEXER
# ============================================================

class DocumentIndexer:

    def __init__(self):

        print("\nLoading document indexer...")

        self.search_engine = DocumentSearch()

        print("Document indexer ready.")

    # ========================================================
    # FILE HASH
    # ========================================================

    @staticmethod
    def file_hash(path: Path):

        sha256 = hashlib.sha256()

        with open(path, "rb") as file:

            while True:

                data = file.read(
                    1024 * 1024
                )

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()

    # ========================================================
    # DELETE FILE FROM DATABASE
    # ========================================================

    def delete_file(self, path: Path):

        try:

            relative_path = str(
                path.relative_to(
                    DOCUMENT_FOLDER
                )
            )

        except ValueError:

            return

        print(
            f"\nRemoving from knowledge base: "
            f"{relative_path}"
        )

        try:

            self.search_engine.collection.delete(
                where={
                    "source_path": relative_path
                }
            )

            print("Removed successfully.")

        except Exception as error:

            print(
                f"Error removing file: {error}"
            )

    # ========================================================
    # INDEX ONE FILE
    # ========================================================

    def index_file(self, path: Path):

        if not path.exists():
            return

        if not path.is_file():
            return

        extension = path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:

            print(
                f"Skipping unsupported file: "
                f"{path.name}"
            )

            return

        try:

            relative_path = str(
                path.relative_to(
                    DOCUMENT_FOLDER
                )
            )

        except ValueError:

            return

        print(
            f"\nProcessing: {relative_path}"
        )

        try:

            # ------------------------------------------------
            # REMOVE OLD VERSION FIRST
            # ------------------------------------------------

            self.search_engine.collection.delete(
                where={
                    "source_path": relative_path
                }
            )

            # ------------------------------------------------
            # EXTRACT
            # ------------------------------------------------

            extracted = extract_file(
                path
            )

            if not extracted:

                print(
                    "No readable content."
                )

                return

            # ------------------------------------------------
            # CHUNK
            # ------------------------------------------------

            chunks = (
                chunk_extracted_sections(
                    extracted
                )
            )

            if not chunks:

                print(
                    "No chunks created."
                )

                return

            texts = [
                item["text"]
                for item in chunks
            ]

            # ------------------------------------------------
            # EMBEDDINGS
            # ------------------------------------------------

            print(
                f"Creating embeddings for "
                f"{len(texts)} chunks..."
            )

            embeddings = (
                self.search_engine
                .embedding_model
                .encode_many(
                    texts
                )
            )

            # ------------------------------------------------
            # FILE HASH
            # ------------------------------------------------

            file_hash = self.file_hash(
                path
            )

            ids = []

            metadatas = []

            # ------------------------------------------------
            # METADATA
            # ------------------------------------------------

            for i, item in enumerate(
                chunks
            ):

                ids.append(
                    f"{file_hash}_{i}"
                )

                metadata = {

                    "source":
                        path.name,

                    "source_path":
                        relative_path,

                    "file_type":
                        extension,

                    "page":
                        (
                            item.get("page")
                            if item.get("page")
                            is not None
                            else ""
                        ),

                    "location":
                        (
                            item.get("location")
                            if item.get("location")
                            else ""
                        ),

                    "language":
                        (
                            item.get("language")
                            if item.get("language")
                            else ""
                        ),

                    # Temporary classification.
                    "sensitivity":
                        "public",

                    "department":
                        "general",
                }

                metadatas.append(
                    metadata
                )

            # ------------------------------------------------
            # ADD TO DATABASE
            # ------------------------------------------------

            self.search_engine.collection.add(

                ids=ids,

                embeddings=embeddings,

                documents=texts,

                metadatas=metadatas,
            )

            print(
                f"Indexed {len(chunks)} chunks."
            )

        except Exception as error:

            print(
                f"Error processing "
                f"{path.name}: {error}"
            )

    # ========================================================
    # INITIAL INDEX
    # ========================================================

    def index_all(self):

        print(
            "\nChecking existing documents..."
        )

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

            print(
                "No supported documents found."
            )

            return

        for path in files:

            self.index_file(path)

        print(
            "\nInitial document indexing complete."
        )


# ============================================================
# FILE WATCHER
# ============================================================

class DocumentWatcher(
    FileSystemEventHandler
):

    def __init__(self, indexer):

        super().__init__()

        self.indexer = indexer

    def on_created(self, event):

        if event.is_directory:
            return

        path = Path(
            event.src_path
        )

        print(
            f"\nNew file detected: "
            f"{path.name}"
        )

        # Give file-copy operation a moment
        # to finish before reading it.
        time.sleep(1)

        self.indexer.index_file(
            path
        )

    def on_modified(self, event):

        if event.is_directory:
            return

        path = Path(
            event.src_path
        )

        print(
            f"\nFile changed: "
            f"{path.name}"
        )

        time.sleep(1)

        self.indexer.index_file(
            path
        )

    def on_deleted(self, event):

        if event.is_directory:
            return

        path = Path(
            event.src_path
        )

        print(
            f"\nFile deleted: "
            f"{path.name}"
        )

        self.indexer.delete_file(
            path
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LOCAL DOCUMENT WATCHER")
    print("=" * 70)

    # --------------------------------------------------------
    # INITIAL INDEX
    # --------------------------------------------------------

    indexer = DocumentIndexer()

    indexer.index_all()

    # --------------------------------------------------------
    # START WATCHER
    # --------------------------------------------------------

    event_handler = DocumentWatcher(
        indexer
    )

    observer = Observer()

    observer.schedule(
        event_handler,
        str(DOCUMENT_FOLDER),
        recursive=True,
    )

    observer.start()

    print("\n" + "=" * 70)

    print(
        "DOCUMENT WATCHER IS RUNNING"
    )

    print("=" * 70)

    print(
        f"\nWatching:"
        f"\n{DOCUMENT_FOLDER}"
    )

    print(
        "\nAdd, modify, or delete supported files."
    )

    print(
        "The knowledge base will update automatically."
    )

    print(
        "\nPress Ctrl+C to stop."
    )

    # --------------------------------------------------------
    # KEEP PROCESS ALIVE
    # --------------------------------------------------------

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        print(
            "\nStopping document watcher..."
        )

        observer.stop()

    observer.join()

    print(
        "Document watcher stopped."
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()