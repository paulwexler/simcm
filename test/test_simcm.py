"""
test simcm
"""
import pytest
import requests
import simcm


class MockResponse:
    """ A requests.request response.
    Just the parts we need.
    """
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

def test_simcm():
    """ happy path
    """
    passed = False
    with simcm.Simulate(
            target_string='requests.request',
            target_globals=dict(requests=requests),
            response_list=[
                requests.request,
                MockResponse(status_code=500, text='')]):
        response1 = requests.request(method='GET', url='https://pypi.org')
        if (response1.status_code == 200
                and 'content="https://pypi.org/"' in response1.text):
            response2 = requests.request(method='GET', url='http://google.com')
            if response2.status_code == 500:
                print(f'Google down following pypi {response1.status_code}')
                passed = True
    assert passed

def test_queue_not_empty():
    """ queue not empty on exit
    """
    with pytest.raises(simcm.QueueNotEmptyError) as exc:
        with simcm.Simulate(
                target_string='requests.request',
                target_globals=dict(requests=requests),
                response_list=[
                    requests.request,
                    MockResponse(status_code=500, text=''),
                    requests.request]):
            response1 = requests.request(method='GET', url='https://pypi.org')
            if (response1.status_code == 200
                    and 'content="https://pypi.org/"' in response1.text):
                response2 = requests.request(
                        method='GET',
                        url='http://google.com')
                if response2.status_code == 500:
                    print(f'Google down following pypi {response1.status_code}')
    result = str(exc.value)
    expect = 'queue is not empty on exit, qsize=1'
    assert expect == result, f'result: {result}'

def test_empty_on_simulate():
    """ queue empty_on_simulate
    """
    with pytest.raises(simcm.QueueEmptyError) as exc:
        with simcm.Simulate(
                target_string='requests.request',
                target_globals=dict(requests=requests),
                response_list=[
                    requests.request]):
            response1 = requests.request(method='GET', url='https://pypi.org')
            if (response1.status_code == 200
                    and 'content="https://pypi.org/"' in response1.text):
                response2 = requests.request(
                        method='GET',
                        url='http://google.com')
    result = str(exc.value)
    expect = (
            "queue is empty on call to requests.request"
            " with args=()"
            " kwargs={'method': 'GET', 'url': 'http://google.com'}.")
    assert expect == result, f'result: {result}'

if __name__ == '__main__': # pragma: no cover
    test_simcm()
    test_queue_not_empty()
    test_empty_on_simulate()
