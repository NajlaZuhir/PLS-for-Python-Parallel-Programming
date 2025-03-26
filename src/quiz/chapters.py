# src/quiz/chapters.py

"""
Module for handling chapter-to-PDF file mappings and related utilities.
"""

CHAPTER_MAP = {
    "Parallel Programming Architectures and Models": "Chapters/Ch1 - Parallel Programming Architectures and Models.pdf",
    "Thread-based Parallelism": "Chapters/Ch2 - Thread-based Parallelism.pdf",
    "Process-based Parallelism": "Chapters/Ch3 - Process-based Parallelism.pdf",
    "Asynchronous Programming": "Chapters/Ch4 - Asynchronous Programming.pdf",
    "Distributed Python": "Chapters/Ch5 - Distributed Python.pdf",
    "GPU Programming with Python": "Chapters/Ch6 -GPU Programming with Python.pdf",
}

def get_chapter_path(chapter_name: str) -> str:
    """
    Returns the PDF path for the given chapter name.
    Raises KeyError if the chapter isn't found.
    """
    return CHAPTER_MAP[chapter_name]
