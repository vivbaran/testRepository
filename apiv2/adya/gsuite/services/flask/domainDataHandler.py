
from flask_restful import Resource, reqparse, request
from adya.controllers import domainDataController
from adya.common.request_session import RequestSession

class UserGroupTree(Resource):
    def get(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request()
        if req_error:
            return req_error
        auth_token = req_session.get_auth_token()
        user_group_tree = domainDataController.get_user_group_tree(auth_token)
        return req_session.generate_sqlalchemy_response(200, user_group_tree)

class UserApps(Resource):
    def get(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(True,optional_params=["clientId","userEmail"])
        if req_error:
            return req_error
        auth_token = req_session.get_auth_token()
        client_id = req_session.get_req_param('clientId')
        user_email = req_session.get_req_param('userEmail')
        if client_id:
            data = domainDataController.get_users_for_app(auth_token,client_id)
        elif user_email:
            data = domainDataController.get_apps_for_user(auth_token,user_email)
        else:
            data = domainDataController.get_all_apps(auth_token)

        return req_session.generate_sqlalchemy_response(200, data)