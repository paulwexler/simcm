# simcm 2.0.1

`simcm.Simulate` is a context manager
which can simulate responses from external resources.

Use this tool to develop unit tests
which obtain complete coverage
without using the external resource.

While testing there is often
a need to simulate the reponses of calls to external resources.
Perhaps the resource is not available in the test environment,
or there is code which handles exceptional cases
which cannot be triggered on demand.

A good strategy is to implement subordinate methods
so they can be tested in isolation.
Even so, the context required to test a particular method
may be difficult to arrange.

In these cases, a simulator which simulates the response
is simpler to use because it lets the application run as is
and handle the (supposedly) actual response.

### DESCRIPTION
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

### EXAMPLE

When the test is run,
the first GET request is sent
and the actual response is returned.
The second GET request is not sent,
the MockedResponse is returned instead.

#### my_app.py

```
import requests

def my_app():
    response1 = requests.request(
            method='GET',
            url='https://pypi.org')
    if response1.status_code == 200:
        response2 = requests.request(
                method='GET',
                url='http://google.com')
        if reponse2.status_code == 500:
            raise RuntimeError('Google 500')
    else:
        raise RuntimeError('Pypi not 200')
```

#### test\_my\_app.py
```
import pytest
import requests
import simcm

import my_app

class MockedResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text=text

def test_my_app_google_500():
    with pytest.raises(RuntimeError) as exc: 
        with simcm.Simulate(
                target_string='requests.request',
                target_globals=dict(requests=requests),
                response_list=[
                        requests.request,
                        MockedResponse(status_code=500, text='')]):
            my_app.my_app()
    result = str(exc.value)
    expect = 'Google 500'
    assert result == expect, f'result: {result}'
```
### CLASSES
```
    builtins.Exception(builtins.BaseException)
        SimulateError
            QueueEmptyError
            QueueNotEmptyError
    builtins.object
        Simulate
    
    class QueueEmptyError(SimulateError)
     |  queue empty
     |  
     |  Method resolution order:
     |      QueueEmptyError
     |      SimulateError
     |      builtins.Exception
     |      builtins.BaseException
     |      builtins.object
     |  
    class QueueNotEmptyError(SimulateError)
     |  queue not empty
     |  
     |  Method resolution order:
     |      QueueNotEmptyError
     |      SimulateError
     |      builtins.Exception
     |      builtins.BaseException
     |      builtins.object
     |  
    class Simulate(builtins.object)
     |  Simulate(target_string: str, target_globals: dict, response_list: list = None)
     |  
     |  Create a context which replaces the target callable
     |  with self.simulate.
     |  
     |  Methods defined here:
     |  
     |  __enter__(self)
     |      Save target.
     |      Replace target with self.simulate.
     |      Return self.
     |  
     |  __exit__(self, exception_type, exception_value, traceback)
     |      Restore target.
     |      Call queue_not_empty_on_exit if the queue is not empty.
     |  
     |  __init__(self, target_string: str, target_globals: dict, response_list: list = None)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  enqueue(self, response_list=None)
     |      Put response_list items onto self.queue.
     |      Default is self.response_list.
     |  
     |  queue_empty_on_simulate(self, *args, **kwargs)
     |      What to do when the queue is empty
     |      and simulate is called.
     |      Raise QueueEmptyError.
     |  
     |  queue_not_empty_on_exit(self, exception_type, exception_value, traceback)
     |      What to do when the queue is not empty on exit.
     |      Raise QueueNotEmptyError.
     |  
     |  simulate(self, *args, **kwargs)
     |      Interpret the next response.
     |      If it is callable, call it, and return the result;
     |      otherwise return it.
     |  
     |  ----------------------------------------------------------------------
    class SimulateError(builtins.Exception)
     |  base error
     |  
     |  Method resolution order:
     |      SimulateError
     |      builtins.Exception
     |      builtins.BaseException
     |      builtins.object
     |  
```
