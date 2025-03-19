"""
Response caching system for the AI-powered tax law application.
Implements Redis-based caching to speed up frequently asked tax law queries.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Redis, with a fallback to a simple dictionary cache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, falling back to in-memory cache")


class QueryCache:
    """Caches AI responses for tax law queries to improve performance."""
    
    def __init__(self, use_redis: bool = True, 
                 redis_host: str = "localhost", 
                 redis_port: int = 6379,
                 redis_db: int = 0,
                 ttl: int = 3600 * 24 * 7):  # Default 1 week TTL
        """
        Initialize the query cache.
        
        Args:
            use_redis: Whether to use Redis for caching (if available)
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
            ttl: Time-to-live for cache entries in seconds
        """
        self.ttl = ttl
        self.use_redis = use_redis and REDIS_AVAILABLE
        
        if self.use_redis:
            try:
                self.redis = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True
                )
                # Test connection
                self.redis.ping()
                logger.info(f"Successfully connected to Redis at {redis_host}:{redis_port}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {str(e)}. Falling back to in-memory cache.")
                self.use_redis = False
        
        if not self.use_redis:
            # In-memory cache as fallback
            self.memory_cache = {}
    
    def _generate_cache_key(self, query: str, context: Optional[str] = None) -> str:
        """
        Generate a deterministic cache key for a query and its context.
        
        Args:
            query: The preprocessed tax law query
            context: Optional context string to include in the key
            
        Returns:
            A hashed cache key
        """
        # Create a string with query and context if available
        key_content = query.lower().strip()
        
        if context:
            if isinstance(context, list):
                # Sort to ensure consistent keys regardless of order
                context.sort()
                context_str = ", ".join(context)
            else:
                context_str = str(context)
            
            key_content += ":" + context_str
        
        # Create an MD5 hash as the cache key
        cache_key = f"taxai:query:{hashlib.md5(key_content.encode()).hexdigest()}"
        return cache_key
    
    def get(self, query: str, context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response if available.
        
        Args:
            query: The preprocessed tax law query
            context: Optional context used for the query
            
        Returns:
            The cached response or None if not found
        """
        cache_key = self._generate_cache_key(query, context)
        
        if self.use_redis:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return json.loads(cached_data)
        else:
            if cache_key in self.memory_cache:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return self.memory_cache[cache_key]
        
        logger.info(f"Cache miss for query: {query[:50]}...")
        return None
    
    def set(self, query: str, response: Dict[str, Any], 
            context: Optional[str] = None, ttl: Optional[int] = None) -> None:
        """
        Cache a response for future retrieval.
        
        Args:
            query: The preprocessed tax law query
            response: The generated response data
            context: Optional context used for the query
            ttl: Optional custom TTL (time-to-live) in seconds
        """
        cache_key = self._generate_cache_key(query, context)
        
        # Use the instance TTL if none provided
        if ttl is None:
            ttl = self.ttl
        
        if self.use_redis:
            # Serialize the response to JSON
            json_data = json.dumps(response)
            self.redis.setex(cache_key, ttl, json_data)
        else:
            # Store in memory
            self.memory_cache[cache_key] = response
        
        logger.info(f"Cached response for query: {query[:50]}... (TTL: {ttl}s)")
    
    def invalidate(self, query: str, context: Optional[str] = None) -> bool:
        """
        Invalidate a cached response.
        
        Args:
            query: The preprocessed tax law query
            context: Optional context used for the query
            
        Returns:
            True if a cache entry was invalidated, False otherwise
        """
        cache_key = self._generate_cache_key(query, context)
        
        if self.use_redis:
            deleted = self.redis.delete(cache_key)
            return deleted > 0
        else:
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
                return True
            return False
    
    def clear_all(self) -> None:
        """
        Clear all cached responses.
        """
        if self.use_redis:
            # Get all keys with our prefix and delete them
            keys = self.redis.keys("taxai:query:*")
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached queries from Redis")
        else:
            cache_size = len(self.memory_cache)
            self.memory_cache.clear()
            logger.info(f"Cleared {cache_size} cached queries from memory")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if self.use_redis:
            keys = self.redis.keys("taxai:query:*")
            return {
                "type": "redis",
                "size": len(keys),
                "host": self.redis.connection_pool.connection_kwargs.get("host", "unknown"),
                "port": self.redis.connection_pool.connection_kwargs.get("port", "unknown")
            }
        else:
            return {
                "type": "memory",
                "size": len(self.memory_cache)
            }


# Create a singleton cache instance
query_cache = QueryCache(
    use_redis=os.getenv("USE_REDIS_CACHE", "false").lower() == "true",
    redis_host=os.getenv("REDIS_HOST", "localhost"),
    redis_port=int(os.getenv("REDIS_PORT", "6379")),
    redis_db=int(os.getenv("REDIS_DB", "0")),
    ttl=int(os.getenv("CACHE_TTL", str(3600 * 24 * 7)))  # Default 1 week TTL
)
