"""
File system walker for CodeSentinel.

Provides recursive directory scanning with .gitignore support and file filtering.
"""

import os
import pathlib
from typing import Iterator, List, Set, Optional


class FileWalker:
    """
    Recursively scans directories for files to analyze.

    Respects .gitignore-like exclusions and skips binary files while enforcing
    size limits and returning normalized file lists.
    """

    def __init__(
        self,
        exclude_patterns: Optional[List[str]] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB default
    ):
        """
        Initialize the file walker.

        Args:
            exclude_patterns: List of glob/regex patterns to exclude
            max_file_size: Maximum file size in bytes to process
        """
        self.exclude_patterns = exclude_patterns or []
        self.max_file_size = max_file_size
        self._processed_files: Set[pathlib.Path] = set()

    def scan_directory(self, target_path: str) -> Iterator[pathlib.Path]:
        """
        Recursively scan a directory for text files.

        Args:
            target_path: Path to scan (file or directory)

        Yields:
            Path objects for each file to analyze
        """
        target = pathlib.Path(target_path)

        if target.is_file():
            if self._should_process_file(target):
                yield target
            return

        for file_path in target.rglob("*"):
            if file_path.is_file() and self._should_process_file(file_path):
                yield file_path

    def _should_process_file(self, file_path: pathlib.Path) -> bool:
        """
        Determine if a file should be processed.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be processed, False otherwise
        """
        # Check if already processed
        if file_path in self._processed_files:
            return False

        # Check file size
        try:
            if file_path.stat().st_size > self.max_file_size:
                return False
        except OSError:
            return False

        # Check if binary file (placeholder implementation)
        if self._is_binary_file(file_path):
            return False

        # Check exclusion patterns
        if self._is_excluded(file_path):
            return False

        self._processed_files.add(file_path)
        return True

    def _is_binary_file(self, file_path: pathlib.Path) -> bool:
        """
        Check if a file is binary.

        Args:
            file_path: Path to the file

        Returns:
            True if file appears to be binary, False otherwise
        """
        # Placeholder implementation - will be enhanced in Phase 1
        binary_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin', '.jpg', '.png', '.gif', '.pdf'}
        return file_path.suffix.lower() in binary_extensions

    def _is_excluded(self, file_path: pathlib.Path) -> bool:
        """
        Check if a file should be excluded based on patterns.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be excluded, False otherwise
        """
        # Placeholder implementation - will be enhanced in Phase 1
        for pattern in self.exclude_patterns:
            # Simple pattern matching for now
            if pattern in str(file_path):
                return True
        return False

    def get_processed_count(self) -> int:
        """
        Get the number of files processed in the current scan.

        Returns:
            Number of processed files
        """
        return len(self._processed_files)

    def reset(self) -> None:
        """Reset the walker state for a new scan."""
        self._processed_files.clear()