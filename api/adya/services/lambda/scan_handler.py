from adya.datasources.google import scan, permission
from adya.common import utils
from adya.common.request_session import RequestSession
from adya.datasources.google import incremental_scan
from adya.controllers import domain_controller,actions_controller


def start_scan(event, context):
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(
        True, ['isAdmin','dataSourceId', 'domainId', 'serviceAccountEnabled'])
    if req_error:
        return req_error

    domain_controller.start_scan(req_session.get_auth_token(), req_session.get_req_param(
        'domainId'), req_session.get_req_param('dataSourceId'),req_session.get_req_param('isAdmin'),
            req_session.get_req_param('serviceAccountEnabled'))
    return req_session.generate_response(202)

def get_drive_resources(event, context):
    print "started initial gdrive scan"
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(True, ['dataSourceId', 'domainId','ownerEmail'],
                                                         ['nextPageToken','userEmail'])
    if req_error:
        return req_error

    scan.get_resources(req_session.get_auth_token(), req_session.get_req_param('domainId'), 
                req_session.get_req_param('dataSourceId'),req_session.get_req_param('ownerEmail'),
                req_session.get_req_param('nextPageToken'),req_session.get_req_param('userEmail'))
    return req_session.generate_response(202)

def process_drive_resources(event, context):
    print "Processing Data"
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(
        True, ['dataSourceId', 'domainId'],['userEmail', 'is_new_resource', 'notify_app'])
    if req_error:
        return req_error

    is_new_resource = req_session.get_req_param('is_new_resource') or 1
    notify_app = req_session.get_req_param('notify_app') or 0
    scan.process_resource_data(req_session.get_req_param(
        'domainId'), req_session.get_req_param('dataSourceId'), req_session.get_req_param('userEmail'), req_session.get_body(),
        is_new_resource, notify_app)
    return req_session.generate_response(202)


def process_resource_permissions(event, context):
    print "Getting Permission Data"
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(
        True, ['dataSourceId', 'domainId'],['userEmail'])
    if req_error:
        return req_error

    requestdata = req_session.get_body()
    fileIds = requestdata['fileIds']
    domain_id = req_session.get_req_param('domainId')
    datasource_id = req_session.get_req_param('dataSourceId')
    user_email = req_session.get_req_param('userEmail')
    ## creating the instance of scan_permission class
    scan_permisssion_obj = permission.GetPermission(domain_id, datasource_id , fileIds)
    ## calling get permission api
    scan_permisssion_obj.get_permission(user_email)
    return req_session.generate_response(202)


def get_domain_users(event, context):
    print("Getting domain user")
    req_session = RequestSession(event)
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

def process_domain_users(event, context):
    print("Process users data")
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(
        True, ['dataSourceId', 'domainId'])
    if req_error:
        return req_error

    domain_id = req_session.get_req_param('domainId')
    datasource_id = req_session.get_req_param('dataSourceId')

    data = req_session.get_body()
    users_response_data = data.get("usersResponseData")
    scan.processUsers(req_session.get_auth_token(), users_response_data, datasource_id, domain_id)
    return req_session.generate_response(202)


def get_domain_groups(event, context):
    print("Getting domain groups")
    req_session = RequestSession(event)
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

def process_domain_groups(event, context):
    print("Process groups data")
    req_session = RequestSession(event)
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


def get_group_members(event, context):
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(
        True, ['dataSourceId', 'domainId'])
    if req_error:
        return req_error

    data = req_session.get_body()
    domain_id = req_session.get_req_param('domainId')
    datasource_id = req_session.get_req_param('dataSourceId')
    group_keys = data.get('groupKeys')

    scan.get_group_data(req_session.get_auth_token(), domain_id,datasource_id, group_keys)
    return req_session.generate_response(202)


def get_user_app(event,context):
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(
        True, ['dataSourceId', 'domainId'])
    if req_error:
        return req_error

    data = req_session.get_body()
    domain_id = req_session.get_req_param('domainId')
    datasource_id = req_session.get_req_param('dataSourceId')
    user_email_list = data.get('userEmailList')
    scan.get_all_user_app(req_session.get_auth_token(), domain_id,datasource_id, user_email_list)
    return req_session.generate_response(202)    


def revoke_user_app_access(event,context):
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(
        True, ['dataSourceId', "userEmail","clientId"])
    if req_error:
        return req_error

    datasource_id = req_session.get_req_param('dataSourceId')
    user_email = req_session.get_req_param('userEmail')
    client_id = req_session.get_req_param('clientId')
    actions_controller.revoke_user_app_access(req_session.get_auth_token(), datasource_id,user_email,client_id)
    return req_session.generate_response(204)


def subscribe_gdrive_notifications(event, context):
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(True, ["domainId", "dataSourceId"])
    if req_error:
        return req_error

    incremental_scan.subscribe(req_session.get_req_param('domainId'), req_session.get_req_param('dataSourceId'))
    return req_session.generate_response(202)


def process_gdrive_notifications(event, context):
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(False, mandatory_params=[], optional_params=[], headers=['X-Goog-Channel-Token', 'X-Goog-Channel-ID', 'X-Goog-Resource-State'])
    if req_error:
        return req_error

    datasource_id = req_session.get_req_header('X-Goog-Channel-Token')
    channel_id = req_session.get_req_header('X-Goog-Channel-ID')
    notification_type = req_session.get_req_header('X-Goog-Resource-State')
    incremental_scan.process_notifications(notification_type, datasource_id, channel_id)
    return req_session.generate_response(202)


def handle_channel_expiration(event, context):
    req_session = RequestSession(event)
    req_error = req_session.validate_authorized_request(False)
    if req_error:
        return req_error

    response = incremental_scan.handle_channel_expiration()
    return req_session.generate_response(202)



