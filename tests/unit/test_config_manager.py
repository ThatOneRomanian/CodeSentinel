import unittest
import pathlib
import json
import shutil
from typing import Dict, Any
from unittest.mock import patch, MagicMock
import logging

# Assuming ConfigManager is designed to be testable with a specific path
from sentinel.api.config_manager import ConfigManager
from sentinel.api.models import SharedConfig, ScanConfig, ScanOptions, UserPreferences, AIProviderConfig


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing config persistence
        self.temp_dir = pathlib.Path("./temp_config_test")
        self.config_path = self.temp_dir / "codesentinel" / "config.json"
        
        # Ensure directory is clean before starting
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
        self.config_manager = ConfigManager(config_path=self.config_path)

    def tearDown(self):
        # Clean up the temporary directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch('pathlib.Path.home', return_value=pathlib.Path('/mock/home'))
    def test_get_default_config_path(self, mock_home):
        cm = ConfigManager(config_path=None)

        with patch('os.name', 'posix'):
            linux_path = cm._get_default_config_path()
            self.assertEqual(linux_path, pathlib.Path('/mock/home/.config/codesentinel/config.json'))
        
    def test_save_and_load_config_defaults(self):
        # Test saving and loading a default config
        default_config = SharedConfig()
        
        self.assertTrue(self.config_manager.save_config(default_config))
        self.assertTrue(self.config_path.exists())

        loaded_config = self.config_manager.load_config()
        self.assertEqual(loaded_config.scan_defaults.enable_debug, False)
        self.assertEqual(loaded_config.scan_defaults.scan_options.enable_profiling, False)

    def test_save_and_load_with_custom_values(self):
        # Test saving and loading custom values, including boolean flags
        custom_config = SharedConfig(
            scan_defaults=ScanConfig(
                target_path=pathlib.Path("/test/project"),
                enable_ai=True,
                llm_provider="openai",
                enable_debug=True,
                scan_options=ScanOptions(
                    enable_profiling=True,
                    max_file_size=500,
                    exclude_patterns=["temp"]
                )
            )
        )

        self.config_manager.save_config(custom_config)
        loaded_config = self.config_manager.load_config()
        
        self.assertEqual(loaded_config.scan_defaults.target_path, pathlib.Path("/test/project"))
        self.assertEqual(loaded_config.scan_defaults.enable_ai, True)
        self.assertEqual(loaded_config.scan_defaults.enable_debug, True) 
        self.assertEqual(loaded_config.scan_defaults.scan_options.enable_profiling, True) 
        self.assertEqual(loaded_config.scan_defaults.scan_options.max_file_size, 500)
        self.assertIn("temp", loaded_config.scan_defaults.scan_options.exclude_patterns)
        
    def test_load_config_when_file_missing(self):
        # Test loading when config file doesn't exist (should return default)
        loaded_config = self.config_manager.load_config()
        self.assertIsInstance(loaded_config, SharedConfig)
        self.assertEqual(loaded_config.scan_defaults.enable_ai, False)

    def test_load_config_with_corrupted_json(self):
        # Test gracefully handling corrupted JSON
        self.config_manager.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_manager.config_path.write_text("This is not valid JSON {")
        
        # Should log a warning and return default config
        logger_name = 'sentinel.api.config_manager'
        
        with self.assertLogs(logger_name, level='WARNING'):
            loaded_config = self.config_manager.load_config()
        
        self.assertIsInstance(loaded_config, SharedConfig)
        self.assertEqual(loaded_config.scan_defaults.enable_ai, False)
        
    def test_config_serialization_deserialization_round_trip(self):
        # Comprehensive test for full round-trip
        original_config = SharedConfig(
            scan_defaults=ScanConfig(
                target_path=pathlib.Path("/full/path/test"),
                enable_ai=True,
                enable_debug=True,
                scan_options=ScanOptions(
                    enable_profiling=True
                )
            ),
            user_preferences=UserPreferences(theme="light", language="fr"),
            ai_providers={"deepseek": AIProviderConfig("deepseek", api_key="secret")}
        )
        
        self.config_manager.save_config(original_config)
        loaded_config = self.config_manager.load_config()
        
        self.assertEqual(loaded_config.scan_defaults.target_path, original_config.scan_defaults.target_path)
        self.assertEqual(loaded_config.scan_defaults.enable_debug, original_config.scan_defaults.enable_debug)
        self.assertEqual(loaded_config.scan_defaults.scan_options.enable_profiling, original_config.scan_defaults.scan_options.enable_profiling)
        self.assertEqual(loaded_config.user_preferences.language, original_config.user_preferences.language)
        self.assertIn("deepseek", loaded_config.ai_providers)
        self.assertEqual(loaded_config.ai_providers["deepseek"].api_key, "secret")