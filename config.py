from pathlib import Path




BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_FOLDER = BASE_DIR / "documents"
DATABASE_FOLDER = BASE_DIR / "database"

CHROMA_PATH = DATABASE_FOLDER / "chroma"

REGISTRY_PATH = DATABASE_FOLDER / "document_registry.json"



OLLAMA_MODEL = "qwen3:8b"
OLLAMA_HOST = "http://localhost:11434"




EMBEDDING_MODEL = "all-MiniLM-L6-v2"



INITIAL_RETRIEVAL_K = 5
FINAL_RETRIEVAL_K = 3



CHUNK_SIZE = 600
CHUNK_OVERLAP = 100



SUPPORTED_EXTENSIONS = {
    # Documents
    ".pdf",
    ".txt",
    ".docx",

    # Spreadsheets
    ".csv",
    ".xlsx",
    ".xls",

    # Images
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",

    # Video/audio
    ".mp4",
    ".mov",
    ".mkv",
    ".wav",
    ".mp3",

    # Programming
    ".py",
    ".c",
    ".h",
    ".cpp",
    ".cc",
    ".cxx",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".sh",
    ".bash",
    ".sql",
    ".m",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".md",
}



CODE_EXTENSIONS = {
    ".py",
    ".c",
    ".h",
    ".cpp",
    ".cc",
    ".cxx",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".sh",
    ".bash",
    ".sql",
    ".m",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".md",
}



DOCUMENT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

CHROMA_PATH.mkdir(
    parents=True,
    exist_ok=True
)