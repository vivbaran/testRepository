import os
from flask import Flask
from flask_restful import Api
from adya.services.flask.authhandler import googleoauthlogin,googleoauthcallback

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
api = Api(app)

#Add all routes here
api.add_resource(googleoauthlogin, '/googleoauthlogin')
api.add_resource(googleoauthcallback, '/googleoauthcallback')


if __name__ == '__main__':
    app.run(debug=True)