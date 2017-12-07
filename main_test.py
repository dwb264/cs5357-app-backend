from flask import session, Response
from pymongo import MongoClient
import json
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
		


	'''def test_home_status_code(self):
		result = self.app.get('/') 
		self.assertEqual(result.status_code, 200) '''


	def test_index(self):
	    # This is a Flask feature - you can fire up a test client and access your endpoints for unit testing
	    self.app.testing = True

	    #r = self.app.get('/profile')
	    #assert r.status_code == 200
	    #assert 'Hello World' in r.data.decode('utf-8')
	
	def register(self, username, password,types,first_name,last_name,phone,zipcode,payment,vehicle):
		headers = {'content-type': 'application/json'}
    		return self.app.post('/profile',data=json.dumps({'username':username, 'password':password,'type':types,'first_name':first_name,'last_name':last_name,'phone':phone,'zipcode':zipcode,'payment':payment,'vehicle':vehicle}),headers=headers,
	        follow_redirects=True)


    	def test_valid_user_registration(self):
	    response = self.register('abc', 'hello1234','mover','a','d','1234567890','11234','debit','truck')
	    self.assertEqual(response.status_code, 200)
	    self.assertIn(b'Thanks for registering!', response.data)


	def login(self, username, password):
	    """Login helper function"""
	    headers = {'content-type': 'application/json'}
	    return self.app.post('/login', data=json.dumps({
		    'username':username,
		    'password':password
	    }),headers=headers, follow_redirects=True)



		
		
if __name__ == '__main__':
    unittest.main()







