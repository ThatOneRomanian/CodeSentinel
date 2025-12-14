"""
Unit tests for AI Caching Layer in CodeSentinel Phase 2.

Tests the persistent caching system for AI explanations, prompts, and CWE mappings
to minimize LLM API calls and improve performance.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import pytest
import json
import time
import tempfile
import pathlib
from unittest.mock import patch

from sentinel.llm.cache import AICache, cache_get, cache_set, cache_cleanup, get_cache_stats


class TestAICache:
    """Test the AICache class functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = pathlib.Path(self.temp_dir)
        self.cache = AICache(cache_dir=self.cache_dir, default_ttl=3600)  # 1 hour TTL
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_initialization(self):
        """Test AICache initialization."""
        assert self.cache.cache_dir == self.cache_dir
        assert self.cache.default_ttl == 3600
        
        # Check that cache directories are created
        assert (self.cache_dir / "explanations").exists()
        assert (self.cache_dir / "prompts").exists()
        assert (self.cache_dir / "cwe").exists()
    
    def test_generate_key_consistent_hashing(self):
        """Test that generate_key produces consistent hashes."""
        data1 = {"rule_id": "test_rule", "excerpt": "test content"}
        data2 = {"excerpt": "test content", "rule_id": "test_rule"}  # Different order
        
        key1 = self.cache._generate_key(data1)
        key2 = self.cache._generate_key(data2)
        
        # Same data should produce same key regardless of order
        assert key1 == key2
    
    def test_generate_key_different_data(self):
        """Test that different data produces different keys."""
        data1 = {"rule_id": "test_rule1", "excerpt": "content1"}
        data2 = {"rule_id": "test_rule2", "excerpt": "content2"}
        
        key1 = self.cache._generate_key(data1)
        key2 = self.cache._generate_key(data2)
        
        assert key1 != key2
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        test_data = {"explanation": "Test explanation", "risk_score": 7.5}
        
        # Set value
        success = self.cache.cache_set("explanations", test_data, test_data)
        assert success is True
        
        # Get value
        retrieved = self.cache.cache_get("explanations", test_data)
        assert retrieved == test_data
    
    def test_cache_get_nonexistent(self):
        """Test cache_get with nonexistent key."""
        result = self.cache.cache_get("explanations", "nonexistent_key")
        assert result is None
    
    def test_cache_get_expired(self):
        """Test cache_get with expired entry."""
        test_data = {"test": "data"}
        
        # Set with very short TTL
        self.cache.cache_set("explanations", test_data, test_data, ttl=1)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should return None and remove expired entry
        result = self.cache.cache_get("explanations", test_data)
        assert result is None
        
        # Cache file should be removed
        cache_file = self.cache._get_cache_file_path("explanations", self.cache._generate_key(test_data))
        assert not cache_file.exists()
    
    def test_cache_get_corrupted_file(self):
        """Test cache_get with corrupted cache file."""
        test_data = {"test": "data"}
        cache_key = self.cache._generate_key(test_data)
        cache_file = self.cache._get_cache_file_path("explanations", cache_key)
        
        # Create corrupted JSON file
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text("invalid json content")
        
        # Should return None and remove corrupted file
        result = self.cache.cache_get("explanations", test_data)
        assert result is None
        assert not cache_file.exists()
    
    def test_cache_set_different_types(self):
        """Test cache_set with different cache types."""
        test_data = {"test": "data"}
        
        # Set in different cache types
        self.cache.cache_set("explanations", "key1", test_data)
        self.cache.cache_set("prompts", "key2", test_data)
        self.cache.cache_set("cwe", "key3", test_data)
        
        # Verify all are stored separately
        assert self.cache.cache_get("explanations", "key1") == test_data
        assert self.cache.cache_get("prompts", "key2") == test_data
        assert self.cache.cache_get("cwe", "key3") == test_data
    
    def test_cache_cleanup_removes_expired(self):
        """Test cache_cleanup removes expired entries."""
        # Create some expired and non-expired entries
        self.cache.cache_set("explanations", "expired1", "data1", ttl=1)
        self.cache.cache_set("explanations", "expired2", "data2", ttl=1)
        self.cache.cache_set("explanations", "valid1", "data3", ttl=3600)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Run cleanup
        removed_count = self.cache.cache_cleanup("explanations")
        
        assert removed_count == 2  # Should remove 2 expired entries
        
        # Verify only valid entry remains
        assert self.cache.cache_get("explanations", "expired1") is None
        assert self.cache.cache_get("explanations", "expired2") is None
        assert self.cache.cache_get("explanations", "valid1") == "data3"
    
    def test_cache_cleanup_all_types(self):
        """Test cache_cleanup without specific type cleans all caches."""
        # Create expired entries in all cache types
        self.cache.cache_set("explanations", "key1", "data1", ttl=1)
        self.cache.cache_set("prompts", "key2", "data2", ttl=1)
        self.cache.cache_set("cwe", "key3", "data3", ttl=1)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Run cleanup on all types
        removed_count = self.cache.cache_cleanup()
        
        assert removed_count == 3  # Should remove all 3 expired entries
    
    def test_get_stats(self):
        """Test get_stats returns correct statistics."""
        # Create some cache entries
        self.cache.cache_set("explanations", "key1", "data1", ttl=3600)
        self.cache.cache_set("explanations", "key2", "data2", ttl=1)  # Will expire
        self.cache.cache_set("prompts", "key3", "data3", ttl=3600)
        
        # Wait for one to expire
        time.sleep(1.1)
        
        stats = self.cache.get_stats()
        
        assert stats["total_entries"] == 3
        assert stats["expired_entries"] == 1
        assert "explanations" in stats["cache_types"]
        assert "prompts" in stats["cache_types"]
        assert "cwe" in stats["cache_types"]
        
        explanations_stats = stats["cache_types"]["explanations"]
        assert explanations_stats["entries"] == 2
        assert explanations_stats["expired"] == 1


class TestCacheConvenienceFunctions:
    """Test the convenience functions for global cache access."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = pathlib.Path(self.temp_dir)
        
        # Patch the global cache to use our temp directory
        self.patcher = patch('sentinel.llm.cache._default_cache', None)
        self.mock_default_cache = self.patcher.start()
        
        # Create a cache instance for testing convenience functions
        self.cache = AICache(cache_dir=self.cache_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_get_and_set(self):
        """Test cache_get and cache_set convenience functions."""
        test_data = {"explanation": "Test data"}
        
        # Set value
        success = cache_set(test_data, test_data, "explanations")
        assert success is True
        
        # Get value
        retrieved = cache_get(test_data, "explanations")
        assert retrieved == test_data
    
    def test_cache_cleanup_convenience(self):
        """Test cache_cleanup convenience function."""
        # This should not raise an exception
        result = cache_cleanup()
        assert isinstance(result, int)
    
    def test_get_cache_stats_convenience(self):
        """Test get_cache_stats convenience function."""
        stats = get_cache_stats()
        assert isinstance(stats, dict)
        assert "total_entries" in stats
        assert "expired_entries" in stats
        assert "cache_types" in stats
    
    def test_cache_persistence(self):
        """Test that cache persists between instances."""
        test_data = {"test": "persistent_data"}
        
        # Set with first cache instance
        cache1 = AICache(cache_dir=self.cache_dir)
        cache1.cache_set("explanations", test_data, test_data)
        
        # Create new cache instance with same directory
        cache2 = AICache(cache_dir=self.cache_dir)
        retrieved = cache2.cache_get("explanations", test_data)
        
        assert retrieved == test_data
    
    def test_cache_file_structure(self):
        """Test that cache files are stored with correct structure."""
        test_data = {"explanation": "Test explanation"}
        cache_key = self.cache._generate_key(test_data)
        
        # Set value
        self.cache.cache_set("explanations", test_data, test_data)
        
        # Check file exists and has correct structure
        cache_file = self.cache._get_cache_file_path("explanations", cache_key)
        assert cache_file.exists()
        
        with open(cache_file, 'r') as f:
            cache_content = json.load(f)
        
        assert "value" in cache_content
        assert "timestamp" in cache_content
        assert "ttl" in cache_content
        assert "key" in cache_content
        assert "created" in cache_content
        assert cache_content["value"] == test_data
        assert cache_content["key"] == cache_key


class TestCacheEdgeCases:
    """Test edge cases and error handling for the cache."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = pathlib.Path(self.temp_dir)
        self.cache = AICache(cache_dir=self.cache_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_set_unserializable_data(self):
        """Test cache_set with data that can't be serialized to JSON."""
        # Create an object that can't be serialized (like a function)
        unserializable_data = lambda x: x  # Function can't be JSON serialized
        
        success = self.cache.cache_set("explanations", "test_key", unserializable_data)
        assert success is False
    
    def test_cache_set_readonly_directory(self):
        """Test cache_set with readonly directory (should fail gracefully)."""
        import os
        import stat
        
        # Make a subdirectory readonly instead of the main cache directory
        readonly_dir = self.cache_dir / "readonly"
        readonly_dir.mkdir()
        
        # Create cache instance with readonly subdirectory
        cache = AICache(cache_dir=readonly_dir)
        
        # Make the directory readonly after cache initialization
        readonly_dir.chmod(stat.S_IREAD)
        
        try:
            success = cache.cache_set("explanations", "test_key", "test_data")
            # Should fail gracefully
            assert success is False
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    
    def test_cache_get_invalid_cache_type(self):
        """Test cache_get with invalid cache type."""
        result = self.cache.cache_get("invalid_type", "test_key")
        assert result is None
    
    def test_cache_cleanup_nonexistent_directory(self):
        """Test cache_cleanup with nonexistent cache directory."""
        nonexistent_dir = self.cache_dir / "nonexistent"
        cache = AICache(cache_dir=nonexistent_dir)
        
        # Should not raise an exception
        removed_count = cache.cache_cleanup()
        assert removed_count == 0


if __name__ == "__main__":
    pytest.main([__file__])