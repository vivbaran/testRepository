import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

import db_config
from adya.common.constants import urls

from adya.core.services.flask import auth_handler, domain_handler, directory_handler, reports_handler, resource_handler, actions_handler, auditlog_handler, policy_handler
from adya.gsuite.services.flask import oauth_handler, scan_handler, incremental_scan_handler, activities_handler

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
CORS(app)

api = Api(app)


#Add all routes here

## routes releated to google Oauth2

api.add_resource(oauth_handler.google_oauth_request, urls.GOOGLE_OAUTH_LOGIN)
api.add_resource(oauth_handler.google_oauth_callback, urls.GOOGLE_OAUTHCALLBACK_PATH)

api.add_resource(auth_handler.get_user_session, '/common/user')
api.add_resource(reports_handler.DashboardWidget, '/common/widgets')
## routes for scan user data for getting file meta data for each user and get user and group
## meta data for a domain
api.add_resource(scan_handler.DriveScan, urls.SCAN_START)
api.add_resource(scan_handler.DriveResources, urls.SCAN_RESOURCES)
api.add_resource(scan_handler.GetDomainuser, urls.SCAN_DOMAIN_USERS)
api.add_resource(scan_handler.GetDomainGroups, urls.SCAN_DOMAIN_GROUPS)
api.add_resource(scan_handler.GetGroupMembers, urls.SCAN_GROUP_MEMBERS)
api.add_resource(scan_handler.GetUserApp, urls.SCAN_USERS_APP)

api.add_resource(domain_handler.datasource, urls.GET_DATASOURCE_PATH)
api.add_resource(domain_handler.asyncdatasourcedelete, urls.ASYNC_DELETE_DATASOURCE_PATH)
## get user group tree
api.add_resource(directory_handler.UserGroupTree, urls.GET_USER_GROUP_TREE_PATH)
api.add_resource(directory_handler.UserApps, urls.GET_APPS)

# incremental scan
api.add_resource(incremental_scan_handler.subscribe,
                 urls.SUBSCRIBE_GDRIVE_NOTIFICATIONS_PATH)

# get file resource data
api.add_resource(resource_handler.GetResources, urls.GET_RESOURCE_TREE_PATH)


#create scheduled report
api.add_resource(reports_handler.ScheduledReport, urls.GET_SCHEDULED_REPORT_PATH)
#run scheduled report
api.add_resource(reports_handler.RunReport, urls.RUN_SCHEDULED_REPORT)

# activities
api.add_resource(activities_handler.get_activities_for_user,
                 urls.GET_ACTIVITIES_FOR_USER_PATH)

# actions
api.add_resource(actions_handler.get_all_actions, urls.GET_ALL_ACTIONS_PATH)
api.add_resource(actions_handler.initiate_action, urls.INITIATE_ACTION_PATH)

api.add_resource(auditlog_handler.get_audit_log, urls.GET_AUDITLOG_PATH)

#policies
api.add_resource(policy_handler.Policy, urls.POLICIES_PATH)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)