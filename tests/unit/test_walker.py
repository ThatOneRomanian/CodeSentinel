"""
Unit tests for file system walker functionality.

Tests directory walking, file filtering, and path validation for CodeSentinel.
"""

import pytest
import tempfile
import pathlib
from unittest.mock import Mock, patch

from sentinel.scanner.walker import (
    walk_directory,
    validate_target_path,
    _should_include_file,
    DEFAULT_INCLUDE_EXTENSIONS,
    DEFAULT_EXCLUDE_PATTERNS
)


class TestWalker:
    """Test file system walker functionality."""

    def test_validate_target_path_valid_directory(self):
        """Test validating a valid directory path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = validate_target_path(temp_dir)
            assert path.exists()
            assert path.is_dir()

    def test_validate_target_path_valid_file(self):
        """Test validating a valid file path."""
        with tempfile.NamedTemporaryFile() as temp_file:
            path = validate_target_path(temp_file.name)
            assert path.exists()
            assert path.is_file()

    def test_validate_target_path_nonexistent(self):
        """Test validating a nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            validate_target_path("/nonexistent/path/that/does/not/exist")

    def test_validate_target_path_empty(self):
        """Test validating an empty path raises ValueError."""
        with pytest.raises(ValueError):
            validate_target_path("")

    def test_walk_directory_single_file(self):
        """Test walking a single file."""
        with tempfile.NamedTemporaryFile(suffix='.py') as temp_file:
            files = walk_directory(pathlib.Path(temp_file.name))
            assert len(files) == 1
            assert files[0] == pathlib.Path(temp_file.name)

    def test_walk_directory_recursive(self):
        """Test recursive directory walking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            
            # Create test files
            (temp_path / "file1.py").write_text("test")
            (temp_path / "file2.js").write_text("test")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "file3.py").write_text("test")
            
            files = walk_directory(temp_path)
            file_names = [f.name for f in files]
            
            assert len(files) == 3
            assert "file1.py" in file_names
            assert "file2.js" in file_names
            assert "file3.py" in file_names

    def test_walk_directory_exclude_patterns(self):
        """Test that exclude patterns work correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            
            # Create files that should be excluded
            (temp_path / ".git").mkdir()
            (temp_path / ".git" / "config").write_text("test")
            (temp_path / "__pycache__").mkdir()
            (temp_path / "__pycache__" / "file.pyc").write_text("test")
            (temp_path / "node_modules").mkdir()
            (temp_path / "node_modules" / "package.json").write_text("test")
            
            # Create files that should be included
            (temp_path / "app.py").write_text("test")
            (temp_path / "config.js").write_text("test")
            
            files = walk_directory(temp_path)
            file_names = [f.name for f in files]
            
            assert len(files) == 2
            assert "app.py" in file_names
            assert "config.js" in file_names
            assert "config" not in file_names
            assert "file.pyc" not in file_names
            assert "package.json" not in file_names

    def test_walk_directory_include_extensions(self):
        """Test that file extension filtering works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            
            # Create files with various extensions
            (temp_path / "app.py").write_text("test")
            (temp_path / "config.js").write_text("test")
            (temp_path / "data.txt").write_text("test")
            (temp_path / "image.png").write_text("test")  # Should be excluded
            (temp_path / "binary.exe").write_text("test")  # Should be excluded
            
            files = walk_directory(temp_path)
            file_names = [f.name for f in files]
            
            assert len(files) == 3
            assert "app.py" in file_names
            assert "config.js" in file_names
            assert "data.txt" in file_names
            assert "image.png" not in file_names
            assert "binary.exe" not in file_names

    def test_walk_directory_custom_extensions(self):
        """Test walking with custom include extensions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            
            (temp_path / "app.py").write_text("test")
            (temp_path / "config.js").write_text("test")
            (temp_path / "data.txt").write_text("test")
            (temp_path / "custom.xyz").write_text("test")
            
            # Only include .xyz files
            custom_extensions = {'.xyz'}
            files = walk_directory(temp_path, include_extensions=custom_extensions)
            
            assert len(files) == 1
            assert files[0].name == "custom.xyz"

    def test_walk_directory_custom_exclude_patterns(self):
        """Test walking with custom exclude patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            
            (temp_path / "app.py").write_text("test")
            (temp_path / "secret.py").write_text("test")
            (temp_path / "test.py").write_text("test")
            
            # Exclude files with 'secret' in the name
            custom_exclude = {'secret'}
            files = walk_directory(temp_path, exclude_patterns=custom_exclude)
            file_names = [f.name for f in files]
            
            assert len(files) == 2
            assert "app.py" in file_names
            assert "test.py" in file_names
            assert "secret.py" not in file_names

    def test_walk_directory_permission_error(self):
        """Test handling of permission errors."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.is_dir') as mock_is_dir, \
             patch('pathlib.Path.rglob') as mock_rglob:
            
            mock_exists.return_value = True
            mock_is_dir.return_value = True
            mock_rglob.side_effect = PermissionError("Permission denied")
            
            with pytest.raises(PermissionError):
                walk_directory(pathlib.Path("/test"))

    def test_walk_directory_nonexistent_path(self):
        """Test walking a nonexistent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            walk_directory(pathlib.Path("/nonexistent/path"))

    def test_walk_directory_non_file_non_directory(self):
        """Test walking a path that is neither file nor directory raises ValueError."""
        # This is tricky to test without creating a special file type
        # We'll test the error case by mocking
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.is_file') as mock_is_file, \
             patch('pathlib.Path.is_dir') as mock_is_dir:
            
            mock_exists.return_value = True
            mock_is_file.return_value = False
            mock_is_dir.return_value = False
            
            with pytest.raises(ValueError):
                walk_directory(pathlib.Path("/special/file"))


class TestShouldIncludeFile:
    """Test file inclusion logic."""

    def test_should_include_file_valid(self):
        """Test that valid files are included."""
        file_path = pathlib.Path("/test/app.py")
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_mode=0o644)
            result = _should_include_file(
                file_path, 
                DEFAULT_INCLUDE_EXTENSIONS, 
                DEFAULT_EXCLUDE_PATTERNS
            )
            assert result is True

    def test_should_include_file_wrong_extension(self):
        """Test that files with wrong extensions are excluded."""
        file_path = pathlib.Path("/test/image.png")
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_mode=0o644)
            result = _should_include_file(
                file_path,
                DEFAULT_INCLUDE_EXTENSIONS,
                DEFAULT_EXCLUDE_PATTERNS
            )
            assert result is False

    def test_should_include_file_excluded_pattern(self):
        """Test that files matching exclude patterns are excluded."""
        file_path = pathlib.Path("/test/.git/config")
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_mode=0o644)
            result = _should_include_file(
                file_path,
                DEFAULT_INCLUDE_EXTENSIONS,
                DEFAULT_EXCLUDE_PATTERNS
            )
            assert result is False

    def test_should_include_file_excluded_extension(self):
        """Test that files with excluded extensions are excluded."""
        file_path = pathlib.Path("/test/file.pyc")
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_mode=0o644)
            result = _should_include_file(
                file_path,
                DEFAULT_INCLUDE_EXTENSIONS,
                DEFAULT_EXCLUDE_PATTERNS
            )
            assert result is False

    def test_should_include_file_custom_extensions(self):
        """Test file inclusion with custom extensions."""
        file_path = pathlib.Path("/test/file.xyz")
        custom_extensions = {'.xyz'}
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_mode=0o644)
            result = _should_include_file(
                file_path,
                custom_extensions,
                DEFAULT_EXCLUDE_PATTERNS
            )
            assert result is True

    def test_should_include_file_custom_exclude(self):
        """Test file inclusion with custom exclude patterns."""
        file_path = pathlib.Path("/test/secret_file.py")
        custom_exclude = {'secret'}
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_mode=0o644)
            result = _should_include_file(
                file_path,
                DEFAULT_INCLUDE_EXTENSIONS,
                custom_exclude
            )
            assert result is False

    def test_should_include_file_unreadable(self):
        """Test that unreadable files are excluded."""
        file_path = pathlib.Path("/test/unreadable.py")
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.side_effect = OSError("Permission denied")
            
            result = _should_include_file(
                file_path,
                DEFAULT_INCLUDE_EXTENSIONS,
                DEFAULT_EXCLUDE_PATTERNS
            )
            assert result is False
