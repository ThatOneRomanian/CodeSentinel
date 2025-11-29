"""
Unit tests for the filetypes language detection module.

Tests the detect_language function with various file extensions and edge cases.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import pathlib
import pytest

from sentinel.utils.filetypes import detect_language


class TestDetectLanguage:
    """Test cases for the detect_language function."""

    def test_detect_python_files(self):
        """Test detection of Python files."""
        assert detect_language(pathlib.Path("app.py")) == "python"
        assert detect_language(pathlib.Path("module.py")) == "python"
        assert detect_language(pathlib.Path("test_file.py")) == "python"

    def test_detect_javascript_files(self):
        """Test detection of JavaScript files."""
        assert detect_language(pathlib.Path("script.js")) == "javascript"
        assert detect_language(pathlib.Path("component.jsx")) == "javascript"

    def test_detect_typescript_files(self):
        """Test detection of TypeScript files."""
        assert detect_language(pathlib.Path("app.ts")) == "typescript"
        assert detect_language(pathlib.Path("component.tsx")) == "typescript"

    def test_detect_config_files(self):
        """Test detection of configuration files."""
        assert detect_language(pathlib.Path("config.yaml")) == "yaml"
        assert detect_language(pathlib.Path("settings.yml")) == "yaml"
        assert detect_language(pathlib.Path("package.json")) == "json"
        assert detect_language(pathlib.Path("pyproject.toml")) == "toml"
        assert detect_language(pathlib.Path("config.ini")) == "ini"

    def test_detect_env_files(self):
        """Test detection of environment files."""
        assert detect_language(pathlib.Path(".env")) == "env"
        assert detect_language(pathlib.Path(".env.production")) == "env"

    def test_detect_shell_scripts(self):
        """Test detection of shell scripts."""
        assert detect_language(pathlib.Path("script.sh")) == "shell"
        assert detect_language(pathlib.Path("setup.bash")) == "shell"

    def test_detect_web_files(self):
        """Test detection of HTML and CSS files."""
        assert detect_language(pathlib.Path("index.html")) == "html"
        assert detect_language(pathlib.Path("style.css")) == "css"

    def test_detect_markdown_files(self):
        """Test detection of Markdown files."""
        assert detect_language(pathlib.Path("README.md")) == "markdown"
        assert detect_language(pathlib.Path("docs.markdown")) == "markdown"

    def test_detect_docker_files(self):
        """Test detection of Docker files."""
        assert detect_language(pathlib.Path("Dockerfile")) == "dockerfile"
        assert detect_language(pathlib.Path("backend.dockerfile")) == "dockerfile"

    def test_detect_makefile(self):
        """Test detection of Makefile."""
        assert detect_language(pathlib.Path("Makefile")) == "makefile"

    def test_detect_other_languages(self):
        """Test detection of various other programming languages."""
        assert detect_language(pathlib.Path("program.c")) == "c"
        assert detect_language(pathlib.Path("header.h")) == "c"
        assert detect_language(pathlib.Path("app.cpp")) == "cpp"
        assert detect_language(pathlib.Path("Main.java")) == "java"
        assert detect_language(pathlib.Path("main.go")) == "go"
        assert detect_language(pathlib.Path("lib.rs")) == "rust"
        assert detect_language(pathlib.Path("index.php")) == "php"
        assert detect_language(pathlib.Path("app.rb")) == "ruby"
        assert detect_language(pathlib.Path("Program.cs")) == "csharp"
        assert detect_language(pathlib.Path("App.swift")) == "swift"
        assert detect_language(pathlib.Path("Main.kt")) == "kotlin"
        assert detect_language(pathlib.Path("Script.scala")) == "scala"

    def test_detect_text_files(self):
        """Test detection of text files."""
        assert detect_language(pathlib.Path("notes.txt")) == "text"
        assert detect_language(pathlib.Path("output.log")) == "text"

    def test_detect_unknown_extensions(self):
        """Test handling of unknown file extensions."""
        assert detect_language(pathlib.Path("unknown.xyz")) is None
        assert detect_language(pathlib.Path("file.custom")) is None
        assert detect_language(pathlib.Path("no_extension")) is None

    def test_case_insensitivity(self):
        """Test that file extension detection is case insensitive."""
        assert detect_language(pathlib.Path("APP.PY")) == "python"
        assert detect_language(pathlib.Path("Config.YAML")) == "yaml"
        assert detect_language(pathlib.Path("package.JSON")) == "json"

    def test_path_with_directories(self):
        """Test detection with full file paths."""
        assert detect_language(pathlib.Path("/home/user/project/app.py")) == "python"
        assert detect_language(pathlib.Path("./src/components/Button.jsx")) == "javascript"
        assert detect_language(pathlib.Path("../config/database.yml")) == "yaml"

    def test_special_filenames(self):
        """Test detection of special filenames without extensions."""
        assert detect_language(pathlib.Path("Dockerfile")) == "dockerfile"
        assert detect_language(pathlib.Path("Makefile")) == "makefile"
        assert detect_language(pathlib.Path("docker-compose.yml")) == "yaml"

    def test_edge_cases(self):
        """Test edge cases and unusual file names."""
        # Files with multiple dots
        assert detect_language(pathlib.Path("app.test.py")) == "python"
        assert detect_language(pathlib.Path("config.prod.yaml")) == "yaml"
        
        # Files starting with dot (hidden files)
        assert detect_language(pathlib.Path(".python_version")) is None
        assert detect_language(pathlib.Path(".env.local")) == "env"
        
        # Empty extension
        assert detect_language(pathlib.Path("file.")) is None

    def test_return_type(self):
        """Test that the function returns the correct type."""
        result = detect_language(pathlib.Path("test.py"))
        assert isinstance(result, str) or result is None
        
        result = detect_language(pathlib.Path("unknown.xyz"))
        assert result is None