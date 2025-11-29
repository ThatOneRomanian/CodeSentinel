"""
AI Caching Layer for CodeSentinel Phase 2.

Provides persistent caching for AI explanations, prompts, and CWE mappings
to minimize LLM API calls and improve performance.

© 2025 Andrei Antonescu. All rights reserved.
Proprietary – not licensed for public redistribution.
"""

import json
import hashlib
import pathlib
import time
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta


class AICache:
    """
    Persistent cache for AI-generated content with TTL support.
    """
    
    def __init__(self, cache_dir: Optional[pathlib.Path] = None, default_ttl: int = 86400):
        """
        Initialize the AI cache.
        
        Args:
            cache_dir: Directory for cache storage. If None, uses default .cache/
            default_ttl: Default time-to-live for cache entries in seconds (default: 24 hours)
        """
        if cache_dir is None:
            cache_dir = pathlib.Path(".cache")
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        
        # Ensure cache directories exist
        self.cache_dir.mkdir(exist_ok=True)
        (self.cache_dir / "explanations").mkdir(exist_ok=True)
        (self.cache_dir / "prompts").mkdir(exist_ok=True)
        (self.cache_dir / "cwe").mkdir(exist_ok=True)
    
    def _generate_key(self, data: Union[str, Dict[str, Any]]) -> str:
        """
        Generate a cache key from input data.
        
        Args:
            data: Input data to generate key from
            
        Returns:
            MD5 hash of the serialized data
        """
        if isinstance(data, dict):
            # Sort dictionary to ensure consistent key generation
            serialized = json.dumps(data, sort_keys=True)
        else:
            serialized = str(data)
        
        return hashlib.md5(serialized.encode('utf-8')).hexdigest()
    
    def _get_cache_file_path(self, cache_type: str, key: str) -> pathlib.Path:
        """
        Get the file path for a cache entry.
        
        Args:
            cache_type: Type of cache (explanations, prompts, cwe)
            key: Cache key
            
        Returns:
            Path to cache file
        """
        return self.cache_dir / cache_type / f"{key}.json"
    
    def _is_expired(self, cache_data: Dict[str, Any]) -> bool:
        """
        Check if cache entry has expired.
        
        Args:
            cache_data: Cache entry data
            
        Returns:
            True if expired, False otherwise
        """
        timestamp = cache_data.get("timestamp")
        ttl = cache_data.get("ttl", self.default_ttl)
        
        if not timestamp:
            return True
        
        expiration_time = timestamp + ttl
        return time.time() > expiration_time
    
    def cache_get(self, cache_type: str, key: Union[str, Dict[str, Any]]) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            cache_type: Type of cache (explanations, prompts, cwe)
            key: Cache key or data to generate key from
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        if isinstance(key, dict):
            cache_key = self._generate_key(key)
        else:
            cache_key = str(key)
        
        cache_file = self._get_cache_file_path(cache_type, cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if expired
            if self._is_expired(cache_data):
                # Remove expired entry
                cache_file.unlink(missing_ok=True)
                return None
            
            return cache_data.get("value")
        
        except (json.JSONDecodeError, IOError, KeyError):
            # Remove corrupted cache file
            cache_file.unlink(missing_ok=True)
            return None
    
    def cache_set(self, cache_type: str, key: Union[str, Dict[str, Any]], value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in the cache.
        
        Args:
            cache_type: Type of cache (explanations, prompts, cwe)
            key: Cache key or data to generate key from
            value: Value to cache
            ttl: Time-to-live in seconds (defaults to instance default)
            
        Returns:
            True if successful, False otherwise
        """
        if isinstance(key, dict):
            cache_key = self._generate_key(key)
        else:
            cache_key = str(key)
        
        cache_file = self._get_cache_file_path(cache_type, cache_key)
        
        cache_data = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl if ttl is not None else self.default_ttl,
            "key": cache_key,
            "created": datetime.now().isoformat()
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, TypeError):
            return False
    
    def cache_cleanup(self, cache_type: Optional[str] = None) -> int:
        """
        Clean up expired cache entries.
        
        Args:
            cache_type: Specific cache type to clean, or None for all
            
        Returns:
            Number of expired entries removed
        """
        removed_count = 0
        
        if cache_type:
            cache_types = [cache_type]
        else:
            cache_types = ["explanations", "prompts", "cwe"]
        
        for ct in cache_types:
            cache_path = self.cache_dir / ct
            if not cache_path.exists():
                continue
            
            for cache_file in cache_path.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if self._is_expired(cache_data):
                        cache_file.unlink()
                        removed_count += 1
                
                except (json.JSONDecodeError, IOError, KeyError):
                    # Remove corrupted cache file
                    cache_file.unlink(missing_ok=True)
                    removed_count += 1
        
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            "total_entries": 0,
            "expired_entries": 0,
            "cache_types": {}
        }
        
        for cache_type in ["explanations", "prompts", "cwe"]:
            cache_path = self.cache_dir / cache_type
            if not cache_path.exists():
                stats["cache_types"][cache_type] = {"entries": 0, "expired": 0}
                continue
            
            entries = 0
            expired = 0
            
            for cache_file in cache_path.glob("*.json"):
                entries += 1
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if self._is_expired(cache_data):
                        expired += 1
                
                except (json.JSONDecodeError, IOError, KeyError):
                    expired += 1
            
            stats["cache_types"][cache_type] = {"entries": entries, "expired": expired}
            stats["total_entries"] += entries
            stats["expired_entries"] += expired
        
        return stats


# Global cache instance
_default_cache: Optional[AICache] = None


def get_cache() -> AICache:
    """
    Get the global cache instance.
    
    Returns:
        Global AICache instance
    """
    global _default_cache
    if _default_cache is None:
        _default_cache = AICache()
    return _default_cache


def cache_get(key: Union[str, Dict[str, Any]], cache_type: str = "explanations") -> Optional[Any]:
    """
    Convenience function to get a value from the global cache.
    
    Args:
        key: Cache key or data to generate key from
        cache_type: Type of cache (explanations, prompts, cwe)
        
    Returns:
        Cached value if found and not expired, None otherwise
    """
    return get_cache().cache_get(cache_type, key)


def cache_set(key: Union[str, Dict[str, Any]], value: Any, cache_type: str = "explanations", ttl: Optional[int] = None) -> bool:
    """
    Convenience function to set a value in the global cache.
    
    Args:
        key: Cache key or data to generate key from
        value: Value to cache
        cache_type: Type of cache (explanations, prompts, cwe)
        ttl: Time-to-live in seconds
        
    Returns:
        True if successful, False otherwise
    """
    return get_cache().cache_set(cache_type, key, value, ttl)


def cache_cleanup(cache_type: Optional[str] = None) -> int:
    """
    Convenience function to clean up expired cache entries.
    
    Args:
        cache_type: Specific cache type to clean, or None for all
        
    Returns:
        Number of expired entries removed
    """
    return get_cache().cache_cleanup(cache_type)


def get_cache_stats() -> Dict[str, Any]:
    """
    Convenience function to get cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    return get_cache().get_stats()