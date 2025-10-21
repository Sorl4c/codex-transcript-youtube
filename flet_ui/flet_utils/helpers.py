from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Optional, Protocol, TypeVar

T = TypeVar("T")


async def run_handler(handler: Optional[Callable[..., Any]], *args: Any, **kwargs: Any) -> Optional[Any]:
    """Execute a handler that might be sync or async."""

    if handler is None:
        return None

    result = handler(*args, **kwargs)
    if asyncio.iscoroutine(result) or isinstance(result, Awaitable):
        return await result  # type: ignore[return-value]
    return result


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    word = singular if count == 1 else plural or f"{singular}s"
    return f"{count} {word}"
