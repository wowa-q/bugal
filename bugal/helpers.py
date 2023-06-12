"""Helpers ib, to provide some useful, but not mandatory functionality
"""
import time


class ExecutionTimer:
    """Execution time measurement, which can be used as decorator
    it can be used like this:
    @ExecutionTimer(repetitions=100)
    def my_function(par):
        function body
    """
    def __init__(self, repetitions=1):
        self.repetitions = repetitions

    def __call__(self, func):
        def timer(*args, **kwargs):
            result = None
            total_time = 0
            print(f"Running {func.__name__}() {self.repetitions} times")
            for _ in range(self.repetitions):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                end = time.perf_counter()
                total_time += end - start
            average_time = total_time / self.repetitions
            print(
                f"{func.__name__}() takes "
                f"{average_time * 1000:.4f} ms on average"
            )
            return result

        return timer
