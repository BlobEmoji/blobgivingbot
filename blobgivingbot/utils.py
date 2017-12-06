# -*- coding: utf-8 -*-

import time


class Timer:
    """Context manager to measure how long the indented block takes to run."""

    def __init__(self):
        self.start: float = None
        self.end: float = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    async def __aenter__(self):
        return self.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)

    def __str__(self):
        return f'{self.duration:.3f}ms'

    @property
    def duration(self):
        """Duration in ms."""
        return (self.end - self.start) * 1000
