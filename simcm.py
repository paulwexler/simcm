"""
simcm (pronounced "simsim")

Simulate a series of calls to a function with a list of mocked
responses.

The `Simulate` class is a context manager.
On `__enter__`, the target function is replaced with `simulate`
On `__exit__`, the target function is restored.

    with Simulate(
            target_string,
            target_globals,
            response_list):
        test_the_application()

* **target_string**:
    The function to simulate, passed as a string.
* **target_globals**:
    A dict used to resolve any global references in target_string.
* **response_list**:
    The list of responses that `simulate` will return.
    Each element of the list is either a callable (typically the target,
    passed as a function) or a mocked response.

The elements of the `response_list` are put onto a FIFO queue.
`simulate` reads the next element from the queue.
If the element is callable,
it is called with all the arguments
the application had passed to the target,
and the result is returned;
otherwise the element is returned.

There are two events to consider.

1. `simulate` is called, but there is no next element.
   In this case,
   `queue_empty_on_simulate(*args, **kwargs)`
   is called.
   `queue_empty_on_simulate` raises `QueueEmptyError`.
   As an aid in preparing the `response_list`,
   `args` and `kwargs` are included in the exception message.

2. `__exit__` is called, but elements remain in the queue.
   In this case,
   `queue_not_empty_on_exit(exception_type, exception_value, traceback)`
   is called.
   `queue_not_empty_on_exit` raises `QueueNotEmptyError`.
   As an aid in preparing the `response_list`,
   the number of elements remaining in the queue
   is included in the exception message.

Both exceptions are sub-classes of `SimulateError`.

To change this behavior,
sub-class `Simulate`, and overwrite these methods.
If `queue_empty_on_simulate` returns,
it should return a callable or a mocked response.
"""

import asyncio

__version__ = '2.0.1'


class SimulateError(Exception):
    """ base error
    """


class QueueEmptyError(SimulateError):
    """ queue empty
    """


class QueueNotEmptyError(SimulateError):
    """ queue not empty
    """


class Simulate:
    """
    Create a context which replaces the target callable
    with self.simulate.
    """
    def __init__(
            self,
            target_string: str,
            target_globals: dict,
            response_list: list = None):
        self.target_string = target_string
        self.target_globals = target_globals
        self.response_list = response_list
        self.queue = asyncio.Queue()
        self.original_target = None

    def __enter__(self):
        """
        Save target.
        Replace target with self.simulate.
        Return self.
        """
        self.original_target = eval(    # pylint: disable=eval-used
                self.target_string,
                self.target_globals,
                locals())
        exec(   # pylint: disable=exec-used
                f'{self.target_string} = self.simulate',
                self.target_globals,
                locals())
        self.enqueue()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Restore target.
        Call queue_not_empty_on_exit if the queue is not empty.
        """
        exec(   # pylint: disable=exec-used
                f'{self.target_string} = self.original_target',
                self.target_globals,
                locals())
        if not self.queue.empty():
            self.queue_not_empty_on_exit(
                    exception_type,
                    exception_value,
                    traceback)

    def enqueue(self, response_list=None):
        """ Put response_list items onto self.queue.
        Default is self.response_list.
        """
        response_list = (
                self.response_list
                if response_list is None
                else response_list)
        for response in response_list:
            self.queue.put_nowait(response)

    def queue_empty_on_simulate(self, *args, **kwargs):
        """ What to do when the queue is empty
        and simulate is called.
        Raise QueueEmptyError.
        """
        raise QueueEmptyError(
                f'queue is empty on call to {self.target_string}'
                f' with args={args} kwargs={kwargs}.')

    def queue_not_empty_on_exit(
            self,
            exception_type,
            exception_value,
            traceback):
        """ What to do when the queue is not empty on exit.
        Raise QueueNotEmptyError.
        """
        raise QueueNotEmptyError(
                f'queue is not empty on exit, qsize={self.queue.qsize()}')

    def simulate(self, *args, **kwargs):
        """ Interpret the next response.
        If it is callable, call it, and return the result;
        otherwise return it.
        """
        if self.queue.empty():
            response = self.queue_empty_on_simulate(*args, **kwargs)
        else:
            response = self.queue.get_nowait()
        if callable(response):
            response = response(*args, **kwargs)
        return response
