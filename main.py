import json

from bson import json_util
from flask import Flask, request, Response, session, jsonify
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError
from werkzeug import security
from werkzeug.exceptions import BadRequest, NotFound, UnsupportedMediaType, Unauthorized
from authy.api import AuthyApiClient
#from exceptions import JSONExceptionHandler
from pymongo import MongoClient
import bson.objectid as ObjectId
import datetime
from PIL import Image
import base64
from cStringIO import StringIO
import simplejson as json
import io

# This defines a Flask application
app = Flask(__name__)

# This code here converts Flask's default (HTML) errors to Json errors.
# This is helpful because HTML breaks clients that are expecting JSON
#JSONExceptionHandler(app)

# We configure the app object
#app.config['MONGO_DBNAME'] = 'moving_database'
app.secret_key = 'A0Zr98j/3yX R~XHH!!!jmN]LWX/,?RT2341'

# This initializes PyMongo and makes `mongo` available
#mongo = PyMongo(app)
authy_api = AuthyApiClient('nhC1DZj2WEeGhKqqi1NNvcIrEHAL30W9')

# database schema
#client = MongoClient()
#client = MongoClient('localhost', 27017)
#db = client['moving_database']
#mongoengine.connect('moving_database', host='localhost', port=27017)
DB_NAME = "man_in_van"
DB_HOST = "ds125126.mlab.com"
DB_PORT = 25126
DB_USER = "admin"
DB_PASS = "Hello7777"

connection = MongoClient(DB_HOST, DB_PORT)

db = connection[DB_NAME]
db.authenticate(DB_USER, DB_PASS)

users = db['users']
moverReviews = db['mover_reviews']
jobs = db['jobs']
offers = db['offers']
jobPhotos = db['job_photos']

#######################
##Revised API endpoints
#######################

@app.route('/profile', methods=['POST'])
def add_new_user():
    """
    This method is used to register a new user.
    :return:
    """

    # Bounce any requests that are not JSON type requests
    if not request.is_json:
        raise UnsupportedMediaType()

    # Check that the request body has `username` and `password` properties
    body = request.get_json()
    if body.get('type') is None:
        raise BadRequest('missing user type')
    if body.get('username') is None:
        raise BadRequest('missing username property')
    if body.get('password') is None:
        raise BadRequest('missing password property')
    if body.get('first_name') is None:
        raise BadRequest('missing first name')
    if body.get('last_name') is None:
        raise BadRequest('missing last name')
    if body.get("phone") is None:
        phone = None
    else:
        phone = body.get("phone")
        if len(phone)!=10 or phone.isdigit()==False:
            raise BadRequest("Invalid phone number")
        phone = int(phone)

    if body.get('type') is 'mover': # Certain properties only required for mover
        if body.get('zipcode') is None:
            raise BadRequest('missing zip code')
        else:
            zipcode = body.get('zipcode')
            if len(zipcode)!=5 or zipcode.isdigit()==False:
                raise BadRequest("Invalid zip code")
            zipcode = int(zipcode)
        if body.get('payment') is None:
            raise BadRequest('missing payment type')
        if body.get("vehicle") is None:
            raise BadRequest("Missing vehicle details")

    if body.get("photo") is None:
        #raise BadRequest("Missing photo")
        data = None
    else:
        #data = imageStorage(body.get("photo"))
        data = body.get("photo")

    password_hash = security.generate_password_hash(body.get('password'))

    new_user = { "type": body.get("type"),
                "first_name": body.get("first_name"),
                "last_name":body.get("last_name"),
                "username":body.get("username"),
                "password": password_hash,
                "zipcode":body.get("zipcode"),
                "payment":body.get("payment"),
                "phone": phone,
                "vehicle": body.get("vehicle"),
                "photo": data,
                "verified_phone": False}

    if users.find_one({"username": body.get("username")}):
        raise NotFound('Username already exists')
    else:
        users.insert_one(new_user)

    user = users.find_one({'username': body.get('username')})
    serializable_user_obj = json.loads(json_util.dumps(user))

    session['user'] = serializable_user_obj["_id"]

    # returning serializable_user_obj is necessary to prevent 401 error for users with profile pics
    return Response(serializable_user_obj, status=201)

def imageStorage(photo):
    image = Image.open(photo)
    findExtIndex = photo[::-1].find('.')
    ext = photo[::-1][:findExtIndex][::-1]
    #manipulate image size according to the requirement
    image.thumbnail((100, 100), Image.ANTIALIAS)
    output = StringIO()
    image.save(output, format=ext)
    im_data = output.getvalue()
    data = base64.b64encode(im_data)
    return data


@app.route('/profile', methods = ['PUT'])
def update():
    if session.get('user') is None:
        raise Unauthorized()

    if not request.is_json:
        raise UnsupportedMediaType()

    body = request.get_json()

    if body.get("phone") is not None:

        number = body.get('phone')

        if len(number)==10 and number.isdigit():
            resp =authy_api.phones.verification_start(number, 1, via='sms')

            if resp.content["success"]:
                users.update_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])},{'$set':{'phone':number}})
                
            else:
                return Response("Invalid number",400)

        else:
            raise BadRequest("invalid phone number")


    if body.get("first_name"):
        users.update_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])},{'$set':{'first_name':body.get("first_name")}})

    if body.get("last_name"):
        users.update_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])},{'$set':{'last_name':body.get("last_name")}})

    if body.get("zipcode"):
        users.update_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])},{'$set':{'zipcode':body.get("zipcode")}})

    if body.get("password"):
        password_hash = security.generate_password_hash(body.get('password'))
        users.update_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])},{'$set':{'password':password_hash}})

    if body.get("payment"):
        users.update_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])},{'$set':{'payment':body.get("payment")}})

    if body.get("vehicle"):
        users.update_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])},{'$set':{'vehicle':body.get("vehicle")}})

    serializable_user_obj = json_util.dumps(session.get('user'))

    return Response(serializable_user_obj, 200)


    ##TODO: implement update method

@app.route('/profile', methods = ['GET'])
def get_profile():
    if session.get('user') is None:
        raise Unauthorized()

    user = users.find_one({'_id':ObjectId.ObjectId(session.get('user')['$oid'])})

    response = json_util.dumps(user)

    return response

#the data passed should come from database - check the earlier implementation of the API
def retriveImage(data):
    decodedData = base64.b64decode(data)
    buf = io.BytesIO(decodedData)
    img = Image.open(buf)
    return img


# Get a specific user's profile
@app.route('/profile/<user_id>', methods = ['GET'])
def get_user_profile(user_id):
    if session.get('user') is None:
        raise Unauthorized()

    user = users.find_one({'_id': ObjectId.ObjectId(user_id)}, projection={'password': False}) # Don't return the user's password
    response = json_util.dumps(user)

    return response


@app.route('/verify', methods = ['POST'])
def verifyCode():
    if session.get('user') is None:
        raise Unauthorized()

    body = request.get_json()
    if body.get('code') is None:
        raise BadRequest('missing verification code')

    code = body.get('code')

    phone = users.find_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])})["phone"]

    if phone is None:
        raise BadRequest("No phone number available")
    
    resp = authy_api.phones.verification_check(phone, 1, code)

    if resp.content["success"]:
        users.update_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])},{'$set':{'verified_phone':True}})

        user = users.find_one({'_id':ObjectId.ObjectId(session.get('user')["$oid"])})

        serializable_user_obj = json.loads(json_util.dumps(user))
        session['user'] = serializable_user_obj['_id']

        return Response(status=200)
    else:
        raise BadRequest("Invalid code")


@app.route('/login', methods=['POST'])
def login():
    """
    This method logs the user in by checking username + password
    against the mongo database
    :return:
    """
    # Bounce any requests that are not JSON type requests
    if not request.is_json:
        raise UnsupportedMediaType()

    # Check that the request body has `username` and `password` properties
    body = request.get_json()
    if body.get('type') is None:
        raise BadRequest('missing user type')
    if body.get('username') is None:
        raise BadRequest('missing username property')
    if body.get('password') is None:
        raise BadRequest('missing password property')

    user = users.find_one({'username': body.get('username'), "type": body.get("type")})

    if user is None:
        session.clear()
        raise BadRequest('User not found')
    if not security.check_password_hash(user['password'], body.get('password')):
        session.clear()
        raise BadRequest('Password does not match')
    # TODO: check that the user type matches
    # We don't want someone who registers as one type to be able to log in as the other type

    # this little trick is necessary because MongoDb sends back objects that are
    # CLOSE to json, but not actually JSON (principally the ObjectId is not JSON serializable)
    # so we just convert to json and use `loads` to get a dict
    serializable_user_obj = json.loads(json_util.dumps(user))
    session['user'] = serializable_user_obj["_id"]

    return Response(status=200)


@app.route('/logout')
def logout():
    """
    This 'logs out' the user by clearing the session data
    """
    session.clear()
    return Response(status=200)

@app.route('/jobs', methods=['POST'])
def create_job():
    """
    Create a record in the jobs collection.
    Only possible if the user is logged in!!
    """

    # Bounce any requests that are not JSON type requests
    if not request.is_json:
        raise UnsupportedMediaType()

    if session.get('user') is None:
        raise Unauthorized()

    # Check that the JSON request has the fields you expect
    body = request.get_json()

    if body.get('start_time') is None:
        raise BadRequest('missing start_time property')
    if body.get('end_time') is None:
        raise BadRequest('missing end_time property')
    if body.get('start_address') is None:
        raise BadRequest("missing start address property")
    if body.get('end_address') is None:
        raise BadRequest("missing end address property")
    if body.get("description") is None:
        raise BadRequest("missing description property")
    if body.get("max_price") is None:
        raise BadRequest("missing max price property")
    else:
        try:
            max_price = float(body.get("max_price"))
        except Exception,e:
            raise BadRequest("Invalid max price property")


    # Create a dictionary that will be inserted into Mongo
    job_record = {'start_time': body.get('start_time'), 
                    'end_time': body.get('end_time'),
                    'start_address': body.get('start_address'),
                    'end_address': body.get("end_address"),
                    'max_price': max_price,
                    'description': body.get("description"),
                    'job_status':'Open'}

    job_record.update({'user': ObjectId.ObjectId(session.get('user')['$oid'])})

    # Insert into the mongo collection
    res = jobs.insert_one(job_record)

    return Response(str(res.inserted_id), 200)

@app.route('/jobs', methods=['GET'])
def get_jobs():
    if session.get('user') is None:
        raise Unauthorized()

    user = users.find_one({'_id': ObjectId.ObjectId(session.get('user')['$oid'])})

    if user['type'] == "requester":
        job = jobs.find_one({'user': ObjectId.ObjectId(session.get('user')['$oid']), 'job_status': 'Open'})
        res = json_util.dumps(job)
        return Response(res, 200) # will return None if the user has no open job, this is ok
    else:
        all_jobs = json_util.dumps(jobs.find({'job_status': 'Open'}))
        return Response(all_jobs, 200)

@app.route('/jobs/<jobid>', methods=['GET'])
def job_desc(jobid):
    """
    This method returns job with specific id
    input: job id
    return: job details
    """
    if session.get('user') is None:
        raise Unauthorized()

    try:
        job = jobs.find_one({"_id": ObjectId.ObjectId(jobid)})

        if job != None:
            return Response(json_util.dumps(job), 200)
        else:
            return BadRequest("Invalid job ID")

    except Exception,e:
        return jsonify(status='ERROR',message=str(e))


@app.route('/review', methods=['POST'])
def review():
    """
    This method is used to give mover_reviews
    input: rating
    return:
    """
    # Bounce any requests that are not JSON type requests
    if session.get('user') is None:
        raise Unauthorized()

    if not request.is_json:
        raise UnsupportedMediaType()

    body = request.get_json()

    if body.get('rating') is None:
        raise BadRequest('missing rating property')

    review_score = body.get('rating')
    userId = body.get('moverID')

    if users.find({'_id':ObjectId.ObjectId(userId)}) is None:
        raise BadRequest("invalid User ID")

    rev = {'userId': userId,
            'review_score':review_score}

    moverReviews.insert_one(rev)

    return Response(status=201)


@app.route('/addOffer', methods=['POST'])
def addOffer():
    # Bounce any requests that are not JSON type requests
    if not request.is_json:
        raise UnsupportedMediaType()

    if session.get('user') is None:
        raise Unauthorized()

    body = request.get_json()
    if body.get('job_id') is None:
        raise BadRequest('missing job_id property')
    if body.get('price') is None:
        raise BadRequest('missing price property')
    if body.get('start_time') is None:
        raise BadRequest('missing start_time property')

    job_id = body.get('job_id')
    price =  body.get('price')
    start_time = body.get('start_time')
    userId = session.get('user')["$oid"]

    job = jobs.find_one({"_id":ObjectId.ObjectId(job_id)})

    job = json.loads(json_util.dumps(job))

    if job is None:
        raise BadRequest("invalid Job ID")

    if job["max_price"] < price:
        raise BadRequest("Price out of range")

    offer = {'userId': userId,
                'jobId':job_id,
                'price':price,
                'start_time': start_time
                }

    try:
        offerId = offers.insert_one(offer).inserted_id

        #return jsonify(status='OK',message='inserted successfully')
        #return str(postId)
    except DuplicateKeyError:
        raise NotFound('offer already exists')

    # check that mongo didn't fail
    return Response(status=201)


@app.route('/getOffers/<job_id>', methods = ['GET'])
def getOffers(job_id):
    if session.get('user') is None:
        raise Unauthorized()

    job = jobs.find_one({"_id": ObjectId.ObjectId(job_id), "job_status": "Open"})

    if job is None:
        raise BadRequest("No open jobs with that Job ID")

    return Response(json_util.dumps(offers.find({'jobId': job_id})), 200)


@app.route('/acceptOffer', methods=['POST'])
def acceptOffer():
    """
    This method is used to accept offer
    input: job id, offer id
    return: boolean
    """
    if session.get('user') is None:
        raise Unauthorized()

    if not request.is_json:
        raise UnsupportedMediaType()

    body = request.get_json()

    if body.get('job_id') is None:
        raise BadRequest('missing jobID property')
    if body.get('offerID') is None:
        raise BadRequest('missing offerID property')
    
    jobID = body.get('job_id')
    job = jobs.find_one({"_id":ObjectId.ObjectId(jobID)})

    if job is None:
        raise BadRequest("Invalid Job ID")

    if job["user"] != ObjectId.ObjectId(session.get('user')["$oid"]):
        raise Unauthorized()

    if job["job_status"] != "Open":
        raise BadRequest("Job already taken")

    jobs.update_one({'_id':ObjectId.ObjectId(body.get('job_id'))},{'$set':{"job_status":"Closed"}})

    return Response(200)


# This allows you to run locally.
# When run in GCP, Gunicorn is used instead (see entrypoint in app.yaml) to
# Access the Flack app via WSGI
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081, debug=True)