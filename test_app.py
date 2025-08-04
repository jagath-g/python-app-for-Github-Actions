import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    rv = client.get('/')
    assert b'Hello from Python Flask App!' in rv.data

def test_add_numbers(client):
    rv = client.get('/add/5/3')
    assert b'{"result":8}' in rv.data

    rv = client.get('/add/-10/5')
    assert b'{"result":-5}' in rv.data

def test_add_numbers_fail(client): # An example of a test that might fail for demonstration
    rv = client.get('/add/1/1')
    assert b'{"result":3}' not in rv.data # This test is designed to pass, checking for 2 not 3
    assert b'{"result":2}' in rv.data # This test will pass
