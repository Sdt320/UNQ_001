"""Distributed atomic mutex locking service using Redis SETNX with TTL."""

import asyncio
import time
from typing import Optional
from app.core.config import settings
from app.core.logging import logger

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


class RedisLockService:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis_client = None
        self._in_memory_locks = {}
        self._async_mutex = asyncio.Lock()

    async def get_client(self):
        """Lazy initialization of async Redis client."""
        if self._redis_client is None and aioredis:
            try:
                self._redis_client = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                await self._redis_client.ping()
            except Exception as e:
                logger.warning(f"Live Redis connection failed ({e}). Utilizing in-memory atomic mutex fallback.")
                self._redis_client = False
        return self._redis_client if self._redis_client is not False else None

    async def acquire_job_claim_lock(self, job_id: str, officer_id: str, ttl_seconds: int = 15) -> bool:
        """
        Executes atomic SET lock:job_claim:{job_id} {officer_id} NX EX 15.
        Returns True if lock was won, False if already claimed.
        """
        lock_key = f"lock:job_claim:{job_id}"
        client = await self.get_client()

        if client:
            try:
                # Redis atomic SET with NX (only if not exists) and EX (expire seconds)
                acquired = await client.set(lock_key, officer_id, nx=True, ex=ttl_seconds)
                return bool(acquired)
            except Exception as e:
                logger.error(f"Redis error during acquire_job_claim_lock: {e}")

        # Threadsafe in-memory atomic fallback for tests and standalone mode
        async with self._async_mutex:
            now = time.time()
            # Clean expired locks
            if lock_key in self._in_memory_locks:
                val, expiry = self._in_memory_locks[lock_key]
                if now > expiry:
                    del self._in_memory_locks[lock_key]

            if lock_key not in self._in_memory_locks:
                self._in_memory_locks[lock_key] = (officer_id, now + ttl_seconds)
                return True
            return False

    async def get_lock_holder(self, job_id: str) -> Optional[str]:
        """Returns the officer_id who holds the claim lock, if any."""
        lock_key = f"lock:job_claim:{job_id}"
        client = await self.get_client()

        if client:
            try:
                return await client.get(lock_key)
            except Exception:
                pass

        async with self._async_mutex:
            now = time.time()
            if lock_key in self._in_memory_locks:
                val, expiry = self._in_memory_locks[lock_key]
                if now <= expiry:
                    return val
                else:
                    del self._in_memory_locks[lock_key]
            return None

    async def release_lock(self, job_id: str) -> bool:
        """Releases the lock key."""
        lock_key = f"lock:job_claim:{job_id}"
        client = await self.get_client()

        if client:
            try:
                await client.delete(lock_key)
                return True
            except Exception:
                pass

        async with self._async_mutex:
            if lock_key in self._in_memory_locks:
                del self._in_memory_locks[lock_key]
                return True
            return False


redis_lock_service = RedisLockService()
