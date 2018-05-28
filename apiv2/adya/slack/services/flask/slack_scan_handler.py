from flask_restful import Resource, request

from adya.common.utils.request_session import RequestSession
from adya.slack import scan


class SlackScan(Resource):
    def post(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId'])
        if req_error:
            return req_error

        scan.start_slack_scan(req_session.get_auth_token(), req_session.get_req_param('dataSourceId'), req_session.get_req_param('domainId'))
        return req_session.generate_response(202)


class SlackUsers(Resource):
    def post(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId'])
        if req_error:
            return req_error

        scan.process_slack_users(req_session.get_auth_token(), req_session.get_req_param('dataSourceId'), req_session.get_req_param('domainId'),
                                 req_session.get_body())

        return req_session.generate_response(202)


    def get(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId','domainId'], ['nextCursor'])
        if req_error:
            return req_error

        scan.get_slack_users(req_session.get_auth_token(),
                           req_session.get_req_param('domainId'),
                           req_session.get_req_param('dataSourceId'),
                           req_session.get_req_param('nextCursor'))

        return req_session.generate_response(202)


class SlackChannels(Resource):
    def post(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId'])
        if req_error:
            return req_error

        scan.process_slack_channels(req_session.get_req_param('dataSourceId'), req_session.get_body())

        return req_session.generate_response(202)

    def get(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId'], ['nextCursor'])
        if req_error:
            return req_error

        scan.get_slack_channels(req_session.get_auth_token(),
                           req_session.get_req_param('dataSourceId'),
                           req_session.get_req_param('nextCursor'))

        return req_session.generate_response(202)


class SlackFiles(Resource):
    def post(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'userEmail'])
        if req_error:
            return req_error

        scan.process_slack_files(req_session.get_req_param('dataSourceId'),
                                 req_session.get_req_param('userEmail'),
                                 req_session.get_body())
        return req_session.generate_response(202)

    def get(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId','userId', 'userEmail'], ['nextPageNumber'])
        if req_error:
            return req_error

        scan.get_slack_files(req_session.get_auth_token(),
                           req_session.get_req_param('dataSourceId'),
                           req_session.get_req_param('userId'),
                           req_session.get_req_param('userEmail'),
                           req_session.get_req_param('nextPageNumber'))

        return req_session.generate_response(202)


class SlackApps(Resource):
    def post(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId'],['change_type'])
        if req_error:
            return req_error

        scan.slack_process_apps(req_session.get_req_param('dataSourceId'), req_session.get_req_param('change_type'),
                                req_session.get_body())
        return req_session.generate_response(202)

    def get(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId'], ['page','change_type'])
        if req_error:
            return req_error

        scan.get_slack_apps(req_session.get_auth_token(),
                           req_session.get_req_param('dataSourceId'),
                           req_session.get_req_param('page'),
                            req_session.get_req_param('change_type'))

        return req_session.generate_response(202)
