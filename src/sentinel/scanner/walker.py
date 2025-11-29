"""
File system walker for CodeSentinel.

Recursively discovers files in target directories, applies file type filters,
and returns a list of file paths for scanning according to the Phase 1 specification.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import pathlib
from typing import List, Set, Optional
import logging

logger = logging.getLogger(__name__)


# Default file extensions to scan (text-based source code files)
DEFAULT_INCLUDE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.m', '.mm',
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.xml', '.json', '.yaml',
    '.yml', '.md', '.txt', '.cfg', '.conf', '.ini', '.toml', '.env', '.sh', '.bash',
    '.zsh', '.fish', '.ps1', '.bat', '.cmd', '.sql', '.r', '.m', '.mat', '.jl'
}

# Default files and directories to exclude
DEFAULT_EXCLUDE_PATTERNS = {
    '.git', '__pycache__', '.pytest_cache', '.vscode', '.idea', 'node_modules',
    'build', 'dist', 'target', 'out', 'bin', 'obj', '.next', '.nuxt', '.cache',
    'vendor', 'packages', 'bower_components', 'coverage', '.nyc_output',
    '*.egg-info', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe'
}


def walk_directory(
    target_path: pathlib.Path,
    include_extensions: Optional[Set[str]] = None,
    exclude_patterns: Optional[Set[str]] = None
) -> List[pathlib.Path]:
    """
    Recursively walk directory and collect files matching criteria.

    Args:
        target_path: Directory or file path to scan
        include_extensions: Set of file extensions to include (default: common source code files)
        exclude_patterns: Set of patterns to exclude (default: common build artifacts, cache, etc.)

    Returns:
        List of file paths that match the inclusion criteria and don't match exclusion patterns

    Raises:
        FileNotFoundError: If target_path doesn't exist
        PermissionError: If target_path cannot be accessed
        ValueError: If target_path is not a file or directory
    """
    if include_extensions is None:
        include_extensions = DEFAULT_INCLUDE_EXTENSIONS

    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

    if not target_path.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_path}")

    files: List[pathlib.Path] = []

    if target_path.is_file():
        # Single file mode
        if _should_include_file(target_path, include_extensions, exclude_patterns):
            files.append(target_path)
        return files

    if not target_path.is_dir():
        raise ValueError(f"Target path is not a file or directory: {target_path}")

    # Recursive directory walk
    logger.info(f"Walking directory: {target_path}")

    try:
        for file_path in target_path.rglob('*'):
            if not file_path.is_file():
                continue

            if _should_include_file(file_path, include_extensions, exclude_patterns):
                files.append(file_path)

    except PermissionError as e:
        logger.warning(f"Permission denied while walking directory: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error walking directory: {e}")
        raise

    logger.info(f"Found {len(files)} files to scan")
    return files


def _should_include_file(
    file_path: pathlib.Path,
    include_extensions: Set[str],
    exclude_patterns: Set[str]
) -> bool:
    """
    Determine if a file should be included in scanning based on criteria.

    Args:
        file_path: Path to the file to check
        include_extensions: Set of file extensions to include
        exclude_patterns: Set of patterns to exclude

    Returns:
        True if file should be included, False otherwise
    """
    # Check file extension
    if file_path.suffix.lower() not in include_extensions:
        return False

    # Check exclusion patterns
    file_path_str = str(file_path)
    for pattern in exclude_patterns:
        if pattern.startswith('*'):
            # Pattern like "*.pyc" - check file extension
            if file_path_str.endswith(pattern[1:]):
                return False
        elif pattern in file_path_str:
            # Pattern like ".git" - check if it appears anywhere in the path
            return False

    # Check if file is readable
    try:
        file_path.stat()
        return True
    except (OSError, IOError):
        logger.debug(f"Cannot access file: {file_path}")
        return False


def validate_target_path(target_path: str) -> pathlib.Path:
    """
    Validate and normalize a target path string.

    Args:
        target_path: String path to validate

    Returns:
        Normalized Path object

    Raises:
        FileNotFoundError: If path doesn't exist
        ValueError: If path is invalid
    """
    if not target_path:
        raise ValueError("Target path cannot be empty")

    path = pathlib.Path(target_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_path}")

    return path
