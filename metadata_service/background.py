from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from threading import Lock


class BackgroundScheduler:
    def __init__(self, max_workers: int) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._in_flight_urls: set[str] = set()
        self._lock = Lock()

    def submit_once(self, normalized_url: str, task: Callable[[], None]) -> bool:
        with self._lock:
            if normalized_url in self._in_flight_urls:
                return False
            self._in_flight_urls.add(normalized_url)

        def wrapped_task() -> None:
            try:
                task()
            finally:
                with self._lock:
                    self._in_flight_urls.discard(normalized_url)

        self.executor.submit(wrapped_task)
        return True
