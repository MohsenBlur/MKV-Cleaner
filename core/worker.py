"""Thread pool worker helper for running jobs in the background."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, List, Any

from core.config import DEFAULTS

logger = logging.getLogger("core.worker")


class Worker:
    """Utility class wrapping ``ThreadPoolExecutor`` for background tasks."""
    def __init__(
        self,
        fn: Callable[..., Any],
        args_list: List[tuple],
        max_workers: int = DEFAULTS["max_workers"],
    ) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures: List[Future] = []
        self.fn = fn
        self.args_list = args_list

    def start(self) -> None:
        for args in self.args_list:
            fut = self.executor.submit(self.fn, *args)
            fut.add_done_callback(self._on_done)
            self.futures.append(fut)

    def cancel(self) -> None:
        logger.info("Cancelling tasks...")
        for f in self.futures:
            f.cancel()
        self.executor.shutdown(wait=False)

    def _on_done(self, fut: Future) -> None:
        if fut.cancelled():
            logger.debug("Task cancelled")
        elif err := fut.exception():
            logger.error("Error: %s", err)
        else:
            logger.debug("Completed: %s", fut.result())
