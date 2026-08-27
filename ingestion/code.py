from pathlib import Path


LANGUAGE_MAP = {
    ".py": "Python",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++ Header",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript React",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".html": "HTML",
    ".css": "CSS",
    ".sh": "Shell",
    ".bash": "Bash",
    ".sql": "SQL",
    ".m": "MATLAB/Objective-C",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".xml": "XML",
    ".md": "Markdown",
}


def extract_code(path: Path):
    """
    Read source code as searchable text.

    The code is indexed as knowledge.
    It will later be used by Qwen to explain
    architecture, logic and concepts.

    This function does NOT execute the code.
    """

    extension = path.suffix.lower()

    language = LANGUAGE_MAP.get(
        extension,
        "Unknown"
    )

    text = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    if not text.strip():
        return []

    return [
        {
            "text": text,
            "page": None,
            "location": f"Source file ({language})",
            "language": language,
        }
    ]