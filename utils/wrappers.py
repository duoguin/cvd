import time, functools
from typing import Callable


class Timer:
    """ timer of a function
    USAGE:
        with Timer("func_name", print=True):
            func()
    """
    def __init__(self, name, print=True):
        self.name = name
        self.print = print

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        if self.print:
            print(f"  <timer> {self.name} took {self.elapsed_time:.4f} seconds")


def retry_wrapper(retry: int = 3, step_name: str = "", log_fn: Callable = print):
    """ 
    USAGE: 
        @retry_wrapper(retry=3, step_name="example_function", log_fn=xxx)
        def example_function(xxx):
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):
            from controller.log import SystemLogger
            for _retry in range(retry):
                try:
                    res = f(*args, **kwargs)
                    return res
                except Exception as e:
                    # Ghi nhận log lỗi vào file hệ thống để kiểm tra nguyên nhân
                    SystemLogger.log(
                        "utils", 
                        step_name or f.__name__, 
                        f"Thử lại {_retry + 1}/{retry} gặp lỗi: {e}", 
                        with_print=False
                    )
                    log_fn(f"  <{step_name}> [retry {_retry + 1}/{retry}] encountered error: {e}")
            else:
                # Rút gọn args/kwargs để tránh làm lỗi hiển thị trên terminal
                clean_args = []
                for arg in args:
                    if isinstance(arg, str) and len(arg) > 200:
                        clean_args.append(arg[:200] + "... [truncated]")
                    else:
                        clean_args.append(arg)
                clean_kwargs = {}
                for k, v in kwargs.items():
                    if isinstance(v, str) and len(v) > 200:
                        clean_kwargs[k] = v[:200] + "... [truncated]"
                    else:
                        clean_kwargs[k] = v
                raise RuntimeError(
                    f"<{step_name}> failed for {retry} times!!! \n  Args: {clean_args}, Kwargs: {clean_kwargs}"
                )
        return wrapped_f
    return decorator