from flask import session, Response

import main
#from main import app
import urllib2
import unittest



def test_index():
    # This is a Flask feature - you can fire up a test client and access your endpoints for unit testing
    main.app.testing = True
    client = main.app.test_client()

    r = client.get('/')
    assert r.status_code == 200
    assert 'Hello World' in r.data.decode('utf-8')



def login(self, username, password):
    """Login helper function"""
    return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)



def logout(self):
    """Logout helper function"""
    return self.app.get('/logout', follow_redirects=True)




def tearDown(self):
	session.clear()
	return Response(status=200)




def test_get_profile(self):
    # sends HTTP GET request to the application
    # on the specified path
    result = self.app.get('/profile') 

    # assert the status code of the response
    self.assertEqual(result.status_code, 200) 




def test_get_jobs(self):
	# sends HTTP GET request to the application
    # on the specified path
    result = self.app.get('/jobs') 

    # assert the status code of the response
    self.assertEqual(result.status_code, 200) 







