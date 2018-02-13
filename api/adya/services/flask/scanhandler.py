from flask_restful import Resource, reqparse, request
from adya.datasources.google import scan, permission
from adya.common import utils
from adya.common.request_session import RequestSession


class DriveResources(Resource):
    def get(self):
        print "started initial gdrive scan"
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId'], ['nextPageToken','userEmail'])
        if req_error:
            return req_error

        scan.get_resources(req_session.get_auth_token(), req_session.get_req_param('domainId'), req_session.get_req_param(
            'dataSourceId'), req_session.get_req_param('userEmail'),req_session.get_req_param('nextPageToken'))
        return req_session.generate_response(202)

    def post(self):
        print "Processing Data"
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId'])
        if req_error:
            return req_error

        scan.process_resource_data(req_session.get_auth_token(), req_session.get_req_param(
            'domainId'), req_session.get_req_param('dataSourceId'), req_session.get_body())
        return req_session.generate_response(202)


class GetPermission(Resource):
    def post(self):
        print "Getting Permission Data"
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId'])
        if req_error:
            return req_error

        requestdata = req_session.get_body()
        fileIds = requestdata['fileIds']
        domain_id = req_session.get_req_param('domainId')
        datasource_id = req_session.get_req_param('dataSourceId')
        ## creating the instance of scan_permission class
        scan_permisssion_obj = permission.GetPermission(domain_id, datasource_id , fileIds)
        ## calling get permission api
        scan_permisssion_obj.get_permission()
        return req_session.generate_response(202)


class GetDomainuser(Resource):
    def get(self):
        print("Getting domain user")
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId'],["nextPageToken"])
        if req_error:
            return req_error

        domain_id = req_session.get_req_param('domainId')
        datasource_id = req_session.get_req_param('dataSourceId')
        next_page_token = req_session.get_req_param('nextPageToken')
        auth_token =  req_session.get_auth_token()

        scan.getDomainUsers(datasource_id, auth_token, domain_id, next_page_token)
        return req_session.generate_response(202)

    def post(self):
        print("Process users data")
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId'])
        if req_error:
            return req_error

        domain_id = req_session.get_req_param('domainId')
        datasource_id = req_session.get_req_param('dataSourceId')

        data = req_session.get_body()
        users_response_data = data.get("usersResponseData")
        scan.processUsers(users_response_data, datasource_id, domain_id)
        return req_session.generate_response(202)


class GetDomainGroups(Resource):
    def get(self):
        print("Getting domain groups")
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId'],["nextPageToken"])
        if req_error:
            return req_error

        domain_id = req_session.get_req_param('domainId')
        datasource_id = req_session.get_req_param('dataSourceId')
        next_page_token = req_session.get_req_param('nextPageToken')
        auth_token =  req_session.get_auth_token()

        scan.getDomainGroups(datasource_id, auth_token , domain_id, next_page_token)
        return req_session.generate_response(202)

    def post(self):
        print("Process groups data")
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId'])
        if req_error:
            return req_error
    
        domain_id = req_session.get_req_param('domainId')
        datasource_id = req_session.get_req_param('dataSourceId')
        auth_token = req_session.get_auth_token()
        data = req_session.get_body()
        group_response_data = data.get("groupsResponseData")

        scan.processGroups(group_response_data, datasource_id ,domain_id, auth_token)
        return req_session.generate_response(202)


class GetGroupMembers(Resource):
    def get(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId','groupKey'],['nextPageToken'])
        if req_error:
            return req_error

        domain_id = req_session.get_req_param('domainId')
        datasource_id = req_session.get_req_param('dataSourceId')
        group_key = req_session.get_req_param('groupKey')
        next_page_token = req_session.get_req_param('nextPageToken')
        auth_token = req_session.get_auth_token()
        scan.getGroupsMember(group_key, auth_token, datasource_id, domain_id, next_page_token)

        return req_session.generate_response(202)
        
    def post(self):
        req_session = RequestSession(request)
        req_error = req_session.validate_authorized_request(
            True, ['dataSourceId', 'domainId', 'groupKey'])
        if req_error:
            return req_error

        data = req_session.get_body()
        domain_id = req_session.get_req_param('domainId')
        datasource_id = req_session.get_req_param('dataSourceId')
        group_key = req_session.get_req_param('groupKey')
        member_response_data = data.get("membersResponseData")

        scan.processGroupMembers(group_key, member_response_data, datasource_id , domain_id)
        return req_session.generate_response(202)
