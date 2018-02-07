import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

import db_config
from adya.services.flask import scanhandler, reports_handler
from adya.common import constants
from adya.services.flask.authhandler import google_oauth_request,google_oauth_callback,get_user_session
from adya.services.flask.domainhandler import datasource
from adya.services.flask.domainDataHandler import UserGroupTree
from adya.services.flask.resourceHandler import GetResources

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
CORS(app)
api = Api(app)

#Add all routes here

## routes releated to google Oauth2

api.add_resource(google_oauth_request, constants.GOOGLE_OAUTH_LOGIN)
api.add_resource(google_oauth_callback, constants.GOOGLE_OAUTHCALLBACK_PATH)

api.add_resource(get_user_session, '/user')
api.add_resource(reports_handler.dashboard_widget, '/widgets')
## routes for scan user data for getting file meta data for each user and get user and group
## meta data for a domain
api.add_resource(scanhandler.initialgdrivescan,constants.INITIAL_GDRIVE_SCAN_PATH)

api.add_resource(scanhandler.processResources,constants.PROCESS_RESOURCES_PATH)
api.add_resource(scanhandler.getPermission, constants.GET_PERMISSION_PATH)

api.add_resource(scanhandler.getdomainuser, constants.GET_DOMAIN_USER_PATH)
api.add_resource(scanhandler.processUsers, constants.PROCESS_USERS_PATH)

api.add_resource(scanhandler.getdomainGroups, constants.GET_DOMAIN_GROUP_PATH)
api.add_resource(scanhandler.processGroups,constants.PROCESS_GROUP_PATH)
api.add_resource(scanhandler.getGroupMembers, constants.GET_GROUP_MEMBERS_PATH)
api.add_resource(scanhandler.processGroupMembers,constants.PROCESS_GROUP_MEMBER_PATH)

api.add_resource(datasource, constants.GET_DATASOURCE_PATH)

## get user group tree
api.add_resource(UserGroupTree, constants.GET_USER_GROUP_TREE_PATH)

# get file resource data
api.add_resource(GetResources,constants.GET_RESOURCE_TREE_PATH)

if __name__ == '__main__':
    app.run(debug=True)