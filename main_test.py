from flask import session, Response


from main import app
import os
#from main import app
import urllib2
import unittest

class MainTestCase(unittest.TestCase):

	def setUp(self):
		# creates a test client
		self.app = app.test_client()
		# propagate the exceptions to the test client
		self.app.testing = True

	def test_home_status_code(self):
		result = self.app.get('/') 
		self.assertEqual(result.status_code, 200) 

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


	def login(self, username, password):
	    """Login helper function"""
	    return main.app.post('/login', data=dict(
		    username=username,
		    password=password
		), follow_redirects=True)

	def logout(self):
	    """Logout helper function"""
	    return main.app.get('/logout', follow_redirects=True)

	def test_index(self):
	    # This is a Flask feature - you can fire up a test client and access your endpoints for unit testing
	    self.app.testing = True

	    r = self.app.get('/')
	    assert r.status_code == 200
	    assert 'Hello World' in r.data.decode('utf-8')


		
		
if __name__ == '__main__':
    unittest.main()







