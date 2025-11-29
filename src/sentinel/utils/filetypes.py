"""
Language detection utilities for CodeSentinel.

Provides lightweight file type detection based on file extensions for
Phase 2+ extensibility and rule applicability filtering.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import pathlib
from typing import Optional


def detect_language(path: pathlib.Path) -> Optional[str]:
    """
    Return a language identifier based on file extension.

    Args:
        path: Path to the file to analyze

    Returns:
        Language identifier such as 'python', 'javascript', 'yaml', 'json', etc.
        Returns None if language cannot be determined from extension.

    Examples:
        >>> detect_language(pathlib.Path('app.py'))
        'python'
        >>> detect_language(pathlib.Path('config.yaml'))
        'yaml'
        >>> detect_language(pathlib.Path('unknown.xyz'))
        None
    """
    # Mapping of common file extensions to language identifiers
    extension_map = {
        # Python files
        '.py': 'python',
        
        # JavaScript/TypeScript files
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        
        # Configuration files
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        
        # Environment files
        '.env': 'env',
        
        # Shell scripts
        '.sh': 'shell',
        '.bash': 'shell',
        '.zsh': 'shell',
        
        # HTML/CSS
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        
        # Markdown
        '.md': 'markdown',
        '.markdown': 'markdown',
        
        # XML
        '.xml': 'xml',
        
        # SQL
        '.sql': 'sql',
        
        # Docker
        '.dockerfile': 'dockerfile',
        'Dockerfile': 'dockerfile',
        
        # Makefile
        'Makefile': 'makefile',
        
        # Text files
        '.txt': 'text',
        '.log': 'text',
        
        # C/C++
        '.c': 'c',
        '.h': 'c',
        '.cpp': 'cpp',
        '.hpp': 'cpp',
        '.cc': 'cpp',
        
        # Java
        '.java': 'java',
        
        # Go
        '.go': 'go',
        
        # Rust
        '.rs': 'rust',
        
        # PHP
        '.php': 'php',
        
        # Ruby
        '.rb': 'ruby',
        
        # C#
        '.cs': 'csharp',
        
        # Swift
        '.swift': 'swift',
        
        # Kotlin
        '.kt': 'kotlin',
        '.kts': 'kotlin',
        
        # Scala
        '.scala': 'scala',
    }
    
    # Handle case where the file name itself is the identifier (e.g., Dockerfile, Makefile)
    file_name = path.name
    
    # Handle environment files with additional extensions (e.g., .env.local, .env.production)
    if file_name.startswith('.env'):
        return 'env'
    
    if file_name in extension_map:
        return extension_map[file_name]
    
    # Get file extension and normalize to lowercase
    extension = path.suffix.lower()
    
    # Return the language identifier if extension is in the map
    return extension_map.get(extension, None)