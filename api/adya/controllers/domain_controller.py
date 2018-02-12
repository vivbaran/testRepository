import json
import datetime
import uuid
from adya.common import utils

from requests_futures.sessions import FuturesSession

from adya.common import constants,utils
from adya.db.connection import db_connection
from adya.db.models import DataSource, LoginUser, Domain, DirectoryStructure, DomainGroup, DomainUser, ResourcePermission, Resource
from adya.datasources.google import gutils


def get_datasource(auth_token, datasource_id):
    session = db_connection().get_session()
    if datasource_id:
        datasources = session.query(DataSource).filter(DataSource.datasource_id == datasource_id). \
            filter(LoginUser.auth_token == auth_token).all()
    else:
        datasources = session.query(DataSource).filter(LoginUser.domain_id == DataSource.domain_id). \
        filter(LoginUser.auth_token == auth_token).all()

    return datasources


def update_datasource(datasource_id, column_name, column_value):
    session = db_connection().get_session()
    if column_name:
        datasources = session.query(DataSource).filter(DataSource.datasource_id == datasource_id). \
            update({column_name: column_name + column_value})
        session.commit()

        return datasources


def create_datasource(auth_token, payload):
    datasource_id = str(uuid.uuid4())
    session = db_connection().get_session()

    existing_user = session.query(LoginUser).filter(LoginUser.auth_token == auth_token).first()
    if existing_user:
        datasource = DataSource()
        datasource.domain_id = existing_user.domain_id
        datasource.datasource_id = datasource_id
        if payload:
            datasource.display_name = payload["display_name"]
        else:
            datasource.display_name = "test"
        # we are fixing the datasoure type this can be obtained from the frontend
        datasource.datasource_type = "GSUITE"
        datasource.creation_time = datetime.datetime.utcnow().isoformat()
        datasource.is_serviceaccount_enabled = gutils.check_if_serviceaccount_enabled(existing_user.email)
        session.add(datasource)
        try:
            session.commit()
        except Exception as ex:
            print (ex)
        print "Starting the scan"
        start_scan(auth_token,datasource.domain_id, datasource.datasource_id)
        return datasource
    else:
        return None

def delete_datasource(auth_token, datasource_id):
    session = db_connection().get_session()

    existing_datasource = session.query(DataSource).filter(DataSource.datasource_id == datasource_id).first()
    domain_id = existing_datasource.domain_id
    if existing_datasource:
        try:
            session.query(DirectoryStructure).filter(DirectoryStructure.datasource_id == datasource_id).delete()
            session.query(DomainGroup).filter(DomainGroup.datasource_id == datasource_id).delete()
            session.query(ResourcePermission).filter(ResourcePermission.datasource_id == datasource_id).delete()
            session.query(Resource).filter(Resource.datasource_id == datasource_id).delete()
            session.query(DomainUser).filter(DomainUser.datasource_id == datasource_id).delete()
            session.delete(existing_datasource)
            session.commit()
        except Exception as ex:
            print "Exception occurred during datasource data delete - " + ex
        
        try:
            gutils.revoke_appaccess(domain_id)
        except Exception as ex:
            print "Exception occurred while revoking the app access - " + ex
    else:
        return None


def create_domain(domain_id, domain_name):
    session = db_connection().get_session()
    creation_time = datetime.datetime.utcnow().isoformat()

    domain = Domain()
    domain.domain_id = domain_id
    domain.domain_name = domain_name
    domain.creation_time = creation_time
    session.add(domain)
    session.commit()
    return domain


def start_scan(auth_token, domain_id, datasource_id):
    query_params = "?domainId=" + domain_id + "&dataSourceId=" + datasource_id
    session = FuturesSession()
    future_users = utils.get_call_with_authorization_header(session,url=constants.SCAN_DOMAIN_USERS + query_params,auth_token=auth_token)
    future_groups = utils.get_call_with_authorization_header(session,url=constants.SCAN_DOMAIN_GROUPS + query_params,auth_token=auth_token)
    future_resources = utils.get_call_with_authorization_header(session,url=constants.SCAN_RESOURCES + query_params,auth_token=auth_token)
    #future_users.result()
    #future_groups.result()
    #future_resources.result()








