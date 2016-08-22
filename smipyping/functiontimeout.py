from functools import wraps
import errno
import os
import signal

class FunctionTimeoutError(Exception):
    pass

def functiontimeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    """Defines a timeout decorator that can be applied other
       functions with the statement @timeout(number-of-seconds).
       Generates a timeout exception if the function execution exceeds the
       timeout time in seconds.
    """  
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise FunctionTimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator

