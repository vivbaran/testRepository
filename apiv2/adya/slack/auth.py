import json
import uuid

import datetime
from slackclient import SlackClient
import slackclient

from adya.common.db import db_utils
from adya.common.db.connection import db_connection
from adya.common.db.models import DataSource, DatasourceCredentials
from adya.common.utils import messaging
from adya.slack import client_credentials

from adya.common.constants import scopeconstants, constants

from adya.common.constants import urls


def request_oauth(scope):
    client_id = client_credentials.client_id
    # try with this client id -  "25151185463.342451215601" (I created slack app for trial)
    scopes = scopeconstants.SLACK_READ_SCOPE
    if scope:
        scopes = scopeconstants.SLACK_SCOPE_DICT[scope]
    return urls.SLACK_ENDPOINT + "?scope={0}&client_id={1}&state={2}".\
                        format(scopes, client_id, scope)


def oauth_callback(auth_code, scope):
    auth_code = auth_code

    # An empty string is a valid token for this request
    sc = SlackClient("")

    # Request the auth tokens from Slack
    auth_response = sc.api_call(
        "oauth.access",
        client_id=client_credentials.client_id,
        client_secret=client_credentials.client_secret,
        code=auth_code
    )
    print auth_response

    access_token = auth_response['access_token']

    # getting the user profile information
    sc = SlackClient(access_token)
    profile_info = sc.api_call("users.profile.get")

    if 'error' in profile_info:
        redirect_url = urls.OAUTH_STATUS_URL + "/error?error={}".format("Credentials not found.")
        return redirect_url

    user_email = profile_info['profile']['email']

    db_session = db_connection().get_session()
    login_user = db_utils.get_login_user_from_email(user_email, db_session)
    datasource_id = str(uuid.uuid4())
    datasource = DataSource()
    datasource.domain_id = login_user.domain_id
    datasource.datasource_id = datasource_id
    datasource.display_name = constants.ConnectorTypes.SLACK

    datasource.creation_time = datetime.datetime.utcnow()
    datasource.datasource_type = constants.ConnectorTypes.SLACK


    db_session.add(datasource)
    db_connection().commit()

    query_params = {"domainId": datasource.domain_id,
                    "dataSourceId": datasource.datasource_id,
                    }

    datasource_credentials = DatasourceCredentials()
    datasource_credentials.datasource_id = datasource.datasource_id
    datasource_credentials.credentials = json.dumps({'domain_id': login_user.domain_id, 'authorize_scope_name': scope, 'token': access_token})
    datasource_credentials.created_user = user_email
    db_session.add(datasource_credentials)
    db_connection().commit()

    messaging.trigger_post_event(urls.SCAN_SLACK_START, login_user.auth_token, query_params, {}, "slack")


    redirect_url = urls.OAUTH_STATUS_URL + "/success?email={}&authtoken={}".format(login_user.domain_id, login_user.auth_token)  # this is temporary just to check wether redirect is working or not TODO : give proper rediect url
    return redirect_url