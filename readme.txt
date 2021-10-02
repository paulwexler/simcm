# simcm @VERSION@

`simcm.Simulate` is a context manager
which is used
to simulate responses from external resources.

Use this tool to develop unit tests
which obtain complete coverage.

While testing there is often
a need to simulate the reponses of calls to external resources.
For example, a GET request is sent to a url and
the response status is expected to be among a set of values,
and the body is expected to have a particular format.
What if it is not?
Perhaps there is code to handle this case.

Suppose while trying to test the application,
the external resource always returns the expected response; 
how can the code that handles the unexpected case be tested?

A good strategy is to implement subordinate methods
so they can be tested in isolation.
Even so, the context required to test a particular method
may be difficult to arrange.

In these cases, a simulator which simulates the unexpected response
is simpler to use because it lets the application run as is
and handle the actual unexpected response.

### DESCRIPTION
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
import simulator

import my_app

class MockedResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text=text

def test_my_app_google_500():
    with pytest.raises(RuntimeError) as exc: 
        with simulator.Simulate(
                target_string='requests.request',
                target_globals=dict(requests=requests),
                response_class=MockedResponse,
                response_list=[
                        requests.request,
                        MockedResponse(status_code=500, text='')]):
            my_app.my_app()
    result = str(exc.value)
    expect = 'Google 500'
    assert result == expect, f'result: {result}'
```
