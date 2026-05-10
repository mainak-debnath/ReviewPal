from __future__ import annotations

import time
from typing import Callable, Iterable, Sequence, TypeVar

from tenacity import RetryCallState, retry, retry_if_exception, stop_after_attempt, wait_exponential

from src.core.config import load_settings


T = TypeVar("T")


def batched(items: Sequence[T], batch_size: int) -> list[list[T]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    return [list(items[index : index + batch_size]) for index in range(0, len(items), batch_size)]


def is_rate_limit_exception(exc: BaseException) -> bool:
    message = str(exc).lower()
    return "429" in message or "rate limit" in message or "resource exhausted" in message


def _before_sleep(retry_state: RetryCallState) -> None:
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    print(
        "Rate limited during indexing write; retrying "
        f"(attempt {retry_state.attempt_number}) after error: {exception}"
    )


def run_rate_limited_write(write_operation: Callable[[], None]) -> None:
    settings = load_settings()

    @retry(
        retry=retry_if_exception(is_rate_limit_exception),
        stop=stop_after_attempt(settings.indexing_max_retries + 1),
        wait=wait_exponential(multiplier=settings.indexing_backoff_base_seconds, min=settings.indexing_backoff_base_seconds),
        before_sleep=_before_sleep,
        reraise=True,
    )
    def _wrapped_write() -> None:
        write_operation()

    _wrapped_write()


def sleep_between_batches() -> None:
    settings = load_settings()
    if settings.indexing_batch_sleep_ms > 0:
        time.sleep(settings.indexing_batch_sleep_ms / 1000)
