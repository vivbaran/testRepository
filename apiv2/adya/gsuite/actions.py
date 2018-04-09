import datetime

import gutils
from adya.common.utils import utils, response_messages
from adya.common.constants import constants
from sqlalchemy import and_
from requests_futures.sessions import FuturesSession
from adya.common.db.connection import db_connection
import json
from adya.common.response_messages import Logger

from adya.common.db.models import DomainUser, Resource


def delete_user_from_group(auth_token, group_email, user_email):
    directory_service = gutils.get_directory_service(auth_token)
    Logger().info("Initiating removal of user {} from group {} ...".format(user_email, group_email))
    try:
        response = directory_service.members().delete(groupKey=group_email, memberKey=user_email).execute()
        return response
        # return response_messages.ResponseMessage(200, "Action completed successfully")
    except Exception as ex:
        content = json.loads(ex.content)
        return content
        # return response_messages.ResponseMessage(ex.resp.status, 'Action failed with error - ' + content['error']['message'])


def add_user_to_group(auth_token, group_email, user_email):
    directory_service = gutils.get_directory_service(auth_token)
    body = {
        "kind": "admin#directory#member",
        "email": user_email,
        "role": "MEMBER"
    }
    Logger().info("Initiating addition of user {} to group {} ...".format(user_email, group_email))
    try:
        response = directory_service.members().insert(groupKey=group_email, body=body).execute()
        return response
        # return response_messages.ResponseMessage(200, "Action completed successfully")
    except Exception as ex:
        content = json.loads(ex.content)
        return  content
        # return response_messages.ResponseMessage(ex.resp.status, 'Action failed with error - ' + content['error']['message'])

def get_applicationDataTransfers_for_gdrive(datatransfer_service):

    results = datatransfer_service.applications().list(maxResults=10).execute()
    applications = results.get('applications', [])
    Logger().info('Applications: {}'.format(applications))
    applicationDataTransfers = []
    if not applications:
        return applicationDataTransfers

    
    for application in applications:
        if application['name'] == 'Drive and Docs':
            applicationDataTransfer = {}
            applicationDataTransfer['applicationId'] = application['id']
            applicationDataTransfer['applicationTransferParams'] = application['transferParams']
            applicationDataTransfers.append(applicationDataTransfer)
            break

    return applicationDataTransfers


def transfer_ownership(auth_token, old_owner_email, new_owner_email):
    datatransfer_service = gutils.get_gdrive_datatransfer_service(auth_token)
    Logger().info("Initiating data transfer...")
    applicationDataTransfers = get_applicationDataTransfers_for_gdrive(datatransfer_service)

    directory_service = gutils.get_directory_service(auth_token)
    old_user_id = directory_service.users().get(userKey=old_owner_email).execute()
    old_user_id = old_user_id.get('id')
    new_user_id = directory_service.users().get(userKey=new_owner_email).execute()
    new_user_id = new_user_id.get('id')

    transfersResource = {"oldOwnerUserId": old_user_id, "newOwnerUserId": new_user_id,
                            "applicationDataTransfers": applicationDataTransfers}

    response = datatransfer_service.transfers().insert(body=transfersResource).execute()
    Logger().info(str(response))
    # handle failure in response
    return response

# This class takes at max 100 resource id and update the permission
# here batch data is an array of resource_id and permissionid/useremail list

class AddOrUpdatePermisssionForResource():
    def __init__(self, auth_token, permissions, owner_email):
        self.permissions = permissions
        self.updated_permissions = []
        self.owner_email = owner_email
        self.change_requests = []
        self.drive_service = gutils.get_gdrive_service(auth_token, owner_email)
        self.exception_message = response_messages.ResponseMessage(200, "Action completed successfully")
        self.batch_number = -1

    def execute(self):
        if len(self.change_requests) == 1:
            try:
                response = self.change_requests[0].execute()
                self.updated_permissions.append(self.permissions[0])
                #return response_messages.ResponseMessage(200, "Action completed successfully")
            except Exception as ex:
                content = json.loads(ex.content)
                self.exception_message = content['error']['message']
            return self.updated_permissions
                #return response_messages.ResponseMessage(ex.resp.status, 'Action failed with error - ' + content['error']['message'])

        else:
            batch_service = self.drive_service.new_batch_http_request(callback=self.batch_request_callback)
            i = 0
            for request in self.change_requests:
                batch_service.add(request)
                i += 1
                if i == 100:
                    self.batch_number += 1
                    batch_service.execute()
                    i = 0
            if i > 0:
                self.batch_number += 1
                batch_service.execute()
            return self.updated_permissions

    def batch_request_callback(self, request_id, response, exception):
        if exception:
            self.exception_message = str(exception)
            Logger().exception("Exception occurred while updating permissions in batch.")
        else:
            index = int(request_id) - 1
            self.updated_permissions.append(self.permissions[(self.batch_number*100) + index])

    def get_exception_message(self):
        return self.exception_message

    def add_permissions(self):
        for permission in self.permissions:
            resource_id = permission.resource_id
            role= permission.permission_type
            add_permission_object = {
                "role": role,
                "type": 'user',
                "emailAddress": permission.email

            }
            request = self.drive_service.permissions().create(fileId=resource_id, body=add_permission_object,
                                                    transferOwnership=True if role=='owner' else False,
                                                              fields='id, emailAddress, type, kind, displayName')
            try:
                response = request.execute()
                permission.permission_id = response['id']
                permission.exposure_type = constants.ResourceExposureType.INTERNAL

                #If the user does not exist in DomainUser table add now
                db_session = db_connection().get_session()

                existing_user = db_session.query(DomainUser).filter(and_(DomainUser.datasource_id == permission.datasource_id,
                    DomainUser.email == permission.email)).first()
                if not existing_user:
                    permission.exposure_type = constants.ResourceExposureType.EXTERNAL
                    domainUser = DomainUser()
                    domainUser.datasource_id = permission.datasource_id
                    domainUser.email = permission.email
                    domainUser.member_type = constants.UserMemberType.EXTERNAL
                    display_name = response['displayName']
                    name = display_name.split(' ')
                    if len(name) > 1:
                        last_name = name[1]
                        domainUser.last_name = last_name
                    elif len(name) > 0:
                        first_name = name[0]
                        domainUser.first_name = first_name
                    db_session.add(domainUser)
                    db_connection().commit()
                self.updated_permissions.append(permission)
            except Exception as ex:
                content = json.loads(ex.content)
                self.exception_message = content['error']['message']
        return self.updated_permissions

    def update_permissions(self):
        for permission in self.permissions:
            resource_id = permission.resource_id
            permission_id = permission.permission_id
            role= permission.permission_type
            update_permission_object = {
                "role": role,
            }
            request = self.drive_service.permissions().update(fileId=resource_id, body=update_permission_object, permissionId=permission_id,
                                                    transferOwnership=True if role=='owner' else False)
            self.change_requests.append(request)
        return self.execute()

    def delete_permissions(self):
        for permission in self.permissions:
            resource_id = permission.resource_id
            permission_id = permission.permission_id
            request = self.drive_service.permissions().delete(fileId=resource_id, permissionId=permission_id,)
            self.change_requests.append(request)
        return self.execute()
