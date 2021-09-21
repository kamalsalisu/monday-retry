import time


class RetryExhaustedException(Exception):
    """Base class for other exceptions"""
    pass


def retry_api_request(action):
    def inner(query=None, timeout=10, retry_count=2, delay=0, error=None):
        # We raise an exception if the retry has been exhausted
        if retry_count <= 0:
            raise RetryExhaustedException(error)
        else:
            time.sleep(delay)
            value = action(query, timeout, retry_count)
            if 'errors' in value:
                return inner(query, timeout, retry_count=retry_count - 1, delay=value['delay'],
                             error=value['errors'])
            else:
                return value

    return inner
