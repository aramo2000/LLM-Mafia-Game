import time
import asyncio
import logging
import functools


def retry(retries=3, delay=1):
    """
    Decorator that retries a function or method until it succeeds or reaches a specified number of attempts.
    :param retries: Number of times to retry the function.
    :param delay: Delay between retries in seconds.
    """

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    logging.warning(
                        f"""
                        Called function {func} FAILED.
                        Retrying in {delay} seconds.
                        Current Attempt: attempts: {attempts}
                        """
                    )
                    attempts += 1
                    if attempts == retries:
                        raise
                    await asyncio.sleep(delay)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    logging.warning(
                        f"""
                        Called function {func} FAILED.
                        Retrying in {delay} seconds.
                        Current Attempt: attempts: {attempts}
                        """
                    )
                    attempts += 1
                    if attempts == retries:
                        raise
                    time.sleep(delay)

        # Check if the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
