import json
from datetime import datetime

from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy import and_

from adya.common.db.models import DomainUser, DomainGroup, Resource, ResourcePermission, DataSource, alchemy_encoder, \
    Application, ApplicationUserAssociation, DirectoryStructure, DatasourceCredentials

from adya.common.db.connection import db_connection

from adya.common.utils import messaging

from adya.common.constants import urls, constants
from adya.common.utils.response_messages import Logger
from adya.slack import slack_utils
from adya.slack.slack_utils import is_external_user


def start_slack_scan(auth_token, datasource_id, domain_id):
    Logger().info(
        "Received the request to start a slack scan for domain_id: {} datasource_id:{} ".format(
            domain_id, datasource_id))
    query_params = {"dataSourceId": datasource_id, "domainId": domain_id}

    messaging.trigger_get_event(urls.SCAN_SLACK_USERS, auth_token, query_params, "slack")
    messaging.trigger_get_event(urls.SCAN_SLACK_CHANNELS, auth_token, query_params, "slack")
    messaging.trigger_get_event(urls.SCAN_SLACK_APPS, auth_token, query_params, "slack")


def get_slack_users(auth_token, domain_id, datasource_id, next_cursor_token=None):
    try:
        slack_client = slack_utils.get_slack_client(datasource_id)
        user_list = slack_client.api_call(
            "users.list",
            limit=150,
            cursor=next_cursor_token
        )

        Logger().info("list of users :  - {}".format(user_list))
        member_list = user_list['members']
        total_memeber_count = len(member_list)
        query_params = {'dataSourceId': datasource_id, "domainId": domain_id}
        get_and_update_scan_count(datasource_id, DataSource.total_user_count, total_memeber_count, auth_token, True)
        # adding user to db
        # TODO: RECONCILIATION
        sentmemeber_count = 0
        while sentmemeber_count < total_memeber_count:
            memebersdata = {}
            memebersdata["users"] = member_list[sentmemeber_count:sentmemeber_count + 30]
            messaging.trigger_post_event(urls.SCAN_SLACK_USERS, auth_token, query_params, memebersdata, "slack")
            sentmemeber_count += 30

        next_cursor_token = user_list['response_metadata']['next_cursor']
        # making new call
        if next_cursor_token:
            query_params["nextCursor"] = next_cursor_token
            messaging.trigger_get_event(urls.SCAN_SLACK_USERS, auth_token, query_params, "slack")
        else:
            get_and_update_scan_count(datasource_id, DataSource.user_scan_status, 1, auth_token, True)
            print "update the values"

    except Exception as ex:
        Logger().exception(
            "Exception occurred while getting data for slack users using next_cursor_token: {}".
                format(next_cursor_token))


def process_slack_users(auth_token, datasource_id, domain_id, memebersdata):
    db_session = db_connection().get_session()

    members_data = memebersdata["users"]
    user_list = []
    user_id_map = {}
    app_list = []
    channels_count = 0
    for member in members_data:
        channels_count = channels_count + 1
        user = {}
        if member['deleted'] or member['is_bot']:
            continue
        profile_info = member['profile']
        user['datasource_id'] = datasource_id
        if 'email' in profile_info:
            user['email'] = profile_info['email']
        else:
            continue

        full_name = profile_info['real_name']
        name_list = full_name.split(" ")
        user['first_name'] = name_list[0]
        user['last_name'] = name_list[1] if len(name_list) > 1 else None
        user['full_name'] = full_name
        user['user_id'] = member['id']
        user['is_admin'] = member['is_admin']
        user['creation_time'] = datetime.fromtimestamp(member['updated']).strftime("%Y-%m-%d %H:%M:%S")
        user['member_type'] = constants.UserMemberType.INTERNAL
        # check for user type

        if is_external_user(domain_id, profile_info['email']):
            user['member_type'] = constants.UserMemberType.EXTERNAL

        user_id_map[member['id']] = profile_info['email']
        user_list.append(user)

    try:
        db_session.bulk_insert_mappings(DomainUser, user_list)
        db_connection().commit()
        get_and_update_scan_count(datasource_id, DataSource.processed_user_count, channels_count, None, True)
    except Exception as ex:
        db_session.rollback()
        # get_and_update_scan_count(datasource_id, DataSource.total_group_count, 0, None, True)
        Logger().exception("Exception occurred while processing data for slack users ex: {}".format(ex))

    for user_id in user_id_map:
        query_params = {'domainId': domain_id, 'dataSourceId': datasource_id,
                        'userId': user_id, 'userEmail': user_id_map[user_id]}
        messaging.trigger_get_event(urls.SCAN_SLACK_FILES, auth_token, query_params, "slack")


def get_slack_channels(auth_token, datasource_id, next_cursor_token=None):
    try:
        slack_client = slack_utils.get_slack_client(datasource_id)
        public_channels = slack_client.api_call("channels.list",
                                                limit=150,
                                                cursor=next_cursor_token
                                                )
        channel_list = public_channels['channels']
        if not next_cursor_token:
            # this api call is being made only for the first time
            private_channels = slack_client.api_call("groups.list")
            private_channel_list = private_channels['groups']
            channel_list.extend(private_channel_list)
            Logger().info("list of private channels :  - {}".format(private_channels))

        Logger().info("list of public channels :  - {}".format(public_channels))

        Logger().info("list of channels :  - {}".format(channel_list))

        query_params = {'dataSourceId': datasource_id}
        # adding channels to db
        # TODO: RECONCILIATION
        total_channel_count = len(channel_list)
        get_and_update_scan_count(datasource_id, DataSource.total_group_count, total_channel_count, auth_token, True)

        sentchannel_count = 0
        while sentchannel_count < total_channel_count:
            channelsdata = {}
            channelsdata["channels"] = channel_list[sentchannel_count:sentchannel_count + 30]
            messaging.trigger_post_event(urls.SCAN_SLACK_CHANNELS, auth_token, query_params, channelsdata, "slack")
            sentchannel_count += 30

        next_cursor_token_for_public_channel = public_channels['response_metadata']['next_cursor']
        if next_cursor_token_for_public_channel:
            query_params = {"dataSourceId": datasource_id, "nextCursor": next_cursor_token}
            messaging.trigger_get_event(urls.SCAN_SLACK_CHANNELS, auth_token, query_params, "slack")

        else:
            get_and_update_scan_count(datasource_id, DataSource.group_scan_status, 1, auth_token,
                                      True)

            print "update the values"

    except Exception as ex:
        # get_and_update_scan_count(datasource_id, DataSource.total_group_count, 0, auth_token, True)
        Logger().exception(
            "Exception occurred while getting data for slack channels using next_cursor_token: {}".
                format(next_cursor_token))


def process_slack_channels(datasource_id, channel_data):
    db_session = db_connection().get_session()
    try:
        group_list = []
        domain_directory_list = []
        channel_list = channel_data["channels"]
        channel_count = 0
        for channel in channel_list:
            channel_count = channel_count + 1
            group = {}

            group['datasource_id'] = datasource_id
            # TODO: Field that should store whether channel is private for public
            group['group_id'] = channel['id']
            group['email'] = channel['name']
            group['name'] = channel['name']
            group['direct_members_count'] = channel['num_members'] if 'num_members' in channel_list else None
            group['include_all_user'] = channel['is_general'] if 'is_general' in channel_list else None
            group_list.append(group)

            creator = channel["creator"]
            group_members = channel["members"]
            for member in group_members:
                domain_directory_struct = {}
                domain_directory_struct['datasource_id'] = datasource_id
                domain_directory_struct['parent_email'] = channel['name']
                domain_directory_struct['member_email'] = member
                domain_directory_struct['member_id'] = member
                domain_directory_struct['member_role'] = "ADMIN" if creator == member else "MEMBER"
                domain_directory_struct["member_type"] = "USER"
                domain_directory_list.append(domain_directory_struct)

        db_session.bulk_insert_mappings(DomainGroup, group_list)
        db_session.bulk_insert_mappings(DirectoryStructure, domain_directory_list)

        db_connection().commit()
        get_and_update_scan_count(datasource_id, DataSource.processed_group_count, channel_count, None, True)

    except Exception as ex:
        db_session.rollback()
        Logger().exception("Exception occurred while processing data for slack channels using ex : {}".format(ex))


def get_slack_files(auth_token, datasource_id, user_id, user_email, page_number_token=None):
    try:
        slack_client = slack_utils.get_slack_client(datasource_id)
        file_list = slack_client.api_call("files.list",
                                          user=user_id,
                                          page=page_number_token)

        files = file_list['files']
        total_file_count = len(files)
        page_number = file_list['paging']['page']
        total_number_of_page = file_list['paging']['pages']

        query_params = {'dataSourceId': datasource_id, "userEmail":user_email}
        get_and_update_scan_count(datasource_id, DataSource.total_file_count, total_file_count, auth_token, True)

        # adding channels to db
        # TODO: RECONCILIATION

        sentfile_count = 0
        while sentfile_count < total_file_count:
            filesdata = {}
            filesdata["files"] = files[sentfile_count:sentfile_count + 30]
            messaging.trigger_post_event(urls.SCAN_SLACK_FILES, auth_token, query_params, filesdata, "slack")
            sentfile_count += 30

        if page_number < total_number_of_page:
            page_number = page_number + 1
            query_params = {"dataSourceId": datasource_id, "nextPageNumber": page_number}
            messaging.trigger_get_event(urls.SCAN_SLACK_FILES, auth_token, query_params, "slack")

        else:
            get_and_update_scan_count(datasource_id, DataSource.file_scan_status, 1, auth_token, True)
            print "update the values"

    except Exception as ex:
        Logger().exception("Exception occurred while processing data for slack files using ex : {}".format(ex))


def process_slack_files(datasource_id, user_email, files_data):
    db_session = db_connection().get_session()
    try:
        resource_list = []
        resource_perms_list = []
        resource_count = 0
        file_list = files_data["files"]
        for file in file_list:
            resource_count = resource_count + 1
            resource = {}
            timestamp = datetime.fromtimestamp(file['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            resource['datasource_id'] = datasource_id
            resource['resource_id'] = file['id']
            resource['resource_name'] = file['name']
            resource['resource_type'] = file['filetype']
            resource['resource_size'] = file['size']
            resource['resource_owner_id'] = user_email
            resource['creation_time'] = timestamp
            resource['last_modified_time'] = timestamp
            resource['web_content_link'] = file['url_private_download'] if 'url_private_download' in file else None
            resource['web_view_link'] = file['url_private'] if 'url_private' in file else None
            is_editable = file["editable"]
            resource_exposure_type = constants.ResourceExposureType.ANYONEWITHLINK if file['public_url_shared']\
                else (constants.ResourceExposureType.DOMAIN if file['is_public'] else
                      constants.ResourceExposureType.PRIVATE)

            # files shared in various ways

            shared_in_channel = file['channels']
            if shared_in_channel:
                permission_exposure_type = constants.ResourceExposureType.DOMAIN
                resource_perms_list = get_resource_permission_map(datasource_id, file, shared_in_channel,
                                                                  permission_exposure_type,
                                                                  resource_perms_list, is_editable)

            shared_in_private_group = file['groups']
            if shared_in_private_group:
                permission_exposure_type = constants.ResourceExposureType.INTERNAL
                resource_perms_list = get_resource_permission_map(datasource_id, file, shared_in_private_group,
                                                                  permission_exposure_type,
                                                                  resource_perms_list, is_editable)

            if resource_exposure_type == constants.ResourceExposureType.ANYONEWITHLINK:
                resource_perms_list = get_resource_permission_map(datasource_id, file, [resource_exposure_type],
                                                                  resource_exposure_type,
                                                                  resource_perms_list, is_editable)


            # shared_in_direct_msgs = file['ims']
            # if shared_in_direct_msgs:
            #     permission_exposure_type = constants.ResourceExposureType.PRIVATE
            #     resource_perms_list = get_resource_permission_map(datasource_id, file, shared_in_direct_msgs,
            #                                                       permission_exposure_type,
            #                                                       resource_perms_list)

            highest_permission_exposure = constants.ResourceExposureType.DOMAIN if shared_in_channel else (
                constants.ResourceExposureType.INTERNAL if shared_in_private_group else constants.ResourceExposureType.PRIVATE)

            resource_exposure_type = slack_utils.get_resource_exposure_type(highest_permission_exposure,
                                                                            resource_exposure_type)

            resource['exposure_type'] = resource_exposure_type
            resource_list.append(resource)

        db_session.bulk_insert_mappings(Resource, resource_list)
        db_session.bulk_insert_mappings(ResourcePermission, resource_perms_list)
        db_connection().commit()
        get_and_update_scan_count(datasource_id, DataSource.processed_file_count, resource_count, None, True)

    except Exception as ex:
        db_session.rollback()
        Logger().exception("Exception occurred while processing data for slack files using ex : {}".format(ex))
        get_and_update_scan_count(datasource_id, DataSource.file_scan_status, 10001, None, True)


def get_resource_permission_map(datasource_id, file, shared_id_list, permission_exposure_type, resource_perms_list, is_editable):
    for shared_id in shared_id_list:
        resource_permission = {}
        resource_permission['datasource_id'] = datasource_id
        resource_permission['resource_id'] = file['id']
        resource_permission['email'] = shared_id
        resource_permission['exposure_type'] = permission_exposure_type
        resource_permission['permission_id'] = shared_id
        resource_permission['permission_type'] = constants.Role.WRITER if is_editable else constants.Role.READER
        resource_perms_list.append(resource_permission)

    return resource_perms_list


def get_slack_apps(auth_token, datasource_id, page=None, change_type=None):
    try:
        slack_client = slack_utils.get_slack_client(datasource_id)
        apps = slack_client.api_call("team.integrationLogs",
                                     limit=150,
                                     page=page,
                                     change_type=slack_utils.AppChangedTypes.REMOVED if (
                                         change_type == slack_utils.AppChangedTypes.REMOVED)
                                     else slack_utils.AppChangedTypes.ADDED
                                     )

        apps_list = apps["logs"]
        total_apps_count = len(apps_list)
        sentapp_count = 0

        query_params = {'dataSourceId': datasource_id}
        if change_type == slack_utils.AppChangedTypes.REMOVED:
            query_params['change_type'] = slack_utils.AppChangedTypes.REMOVED
        else:
            query_params['change_type'] = slack_utils.AppChangedTypes.ADDED

        while sentapp_count < total_apps_count:
            appsdata = {}
            appsdata["apps"] = apps_list[sentapp_count:sentapp_count + 30]
            messaging.trigger_post_event(urls.SCAN_SLACK_APPS, auth_token, query_params, appsdata, "slack")
            sentapp_count += 30

        paging = apps["paging"]
        total_pages = paging["pages"]
        current_page_number = paging["page"]
        if total_pages > current_page_number:
            query_params["page"] = current_page_number + 1
            messaging.trigger_get_event(urls.SCAN_SLACK_APPS, auth_token, query_params, "slack")

        elif change_type != slack_utils.AppChangedTypes.REMOVED:
            query_params["change_type"] = slack_utils.AppChangedTypes.REMOVED
            messaging.trigger_get_event(urls.SCAN_SLACK_APPS, auth_token, query_params, "slack")

    except Exception as ex:
        Logger().exception(
            "Exception occurred while getting data for slack apps using page: {}".
                format(page))


def slack_process_apps(datasource_id, change_type, apps_data):
    db_session = db_connection().get_session()
    try:
        apps_list = apps_data["apps"]
        if change_type == slack_utils.AppChangedTypes.ADDED:
            for app in apps_list:
                id = app["app_id"] if "app_id" in app else app["service_id"]
                timestamp = datetime.strptime(datetime.fromtimestamp(int(app["date"])).strftime('%Y-%m-%d %H:%M:%S'),
                                              '%Y-%m-%d %H:%M:%S')

                scopes = None
                max_score = 0
                if 'scope' in app:
                    scopes = app["scope"]
                    max_score = slack_utils.get_app_score(scopes)

                user_id = app["user_id"]

                existing_app = db_session.query(Application).filter(
                    and_(Application.datasource_id == datasource_id, Application.client_id == id)).first()

                if existing_app:
                    update_app = db_session.query(Application).filter(
                        and_(Application.datasource_id == datasource_id, Application.client_id ==
                             id, Application.timestamp < timestamp)).update({Application.timestamp: timestamp,
                                                                             Application.scopes: scopes,
                                                                             Application.score: max_score},
                                                                            synchronize_session='fetch')

                    if update_app:
                        db_session.query(ApplicationUserAssociation).filter(
                            and_(ApplicationUserAssociation.datasource_id == datasource_id,
                                 ApplicationUserAssociation.client_id ==
                                 id)).update({ApplicationUserAssociation.user_email: user_id},
                                             synchronize_session='fetch')

                else:
                    app_obj = Application()
                    app_obj.datasource_id = datasource_id
                    app_obj.client_id = id
                    app_obj.display_text = app["app_type"] if "app_type" in app else app["service_type"]
                    app_obj.scopes = scopes
                    app_obj.timestamp = timestamp
                    app_obj.score = max_score
                    db_session.add(app_obj)
                    db_connection().commit()

                    user_app_obj = ApplicationUserAssociation()
                    user_app_obj.client_id = id
                    user_app_obj.datasource_id = datasource_id
                    user_app_obj.user_email = user_id
                    db_session.add(user_app_obj)
                    db_connection().commit()

        elif change_type == slack_utils.AppChangedTypes.REMOVED:
            for app in apps_list:
                timestamp = datetime.strptime(datetime.fromtimestamp(int(app["date"])).strftime('%Y-%m-%d %H:%M:%S'),
                                              '%Y-%m-%d %H:%M:%S')
                app = db_session.query(Application).filter(and_(Application.datasource_id == datasource_id,
                                                                Application.timestamp < timestamp)).first()
                if app:
                    db_session.query(ApplicationUserAssociation).filter(
                        and_(ApplicationUserAssociation.datasource_id == datasource_id,
                             ApplicationUserAssociation.client_id == app.client_id)).delete(synchronize_session=False)

                    db_session.delete(app)

        db_connection().commit()

    except Exception as ex:
        db_session.rollback()
        Logger().exception("Exception occurred while processing data for slack apps using ex : {}".format(ex))


def get_and_update_scan_count(datasource_id, column_name, column_value, auth_token=None, send_message=False):
    db_session = db_connection().get_session()
    rows_updated = 0
    try:
        rows_updated = db_session.query(DataSource).filter(DataSource.datasource_id == datasource_id). \
            update({column_name: column_name + column_value})
        db_connection().commit()
    except Exception as ex:
        Logger().exception("Exception occurred while updating the scan status for the datasource.")
        db_session.rollback()

    if rows_updated == 1:
        datasource = db_session.query(DataSource).filter(
            and_(DataSource.datasource_id == datasource_id, DataSource.is_async_delete == False)).first()
        if send_message:
            messaging.send_push_notification("adya-scan-update", json.dumps(datasource, cls=alchemy_encoder()))
        if get_scan_status(datasource) == 1:

            channels_groups = db_session.query(DomainGroup).filter(
                DataSource.datasource_id == datasource_id).all()

            resource_permissions = db_session.query(ResourcePermission).filter(
                ResourcePermission.datasource_id == datasource_id).all()

            channel_id_and_name_map = {}
            # checking for present users and extracting their email id and deleting the removed user from directory structure
            domain_directory_struct = db_session.query(DirectoryStructure).filter(
                DirectoryStructure.datasource_id == datasource_id).all()

            member_to_be_deleted = []
            for member in domain_directory_struct:
                member_id = member.member_id
                existing_member = db_session.query(DomainUser).filter(and_(DomainUser.datasource_id == datasource_id,
                                                                           DomainUser.user_id == member_id)).first()

                is_external_user = False
                if existing_member:
                    member.member_email = existing_member.email
                    # checking if the member is external or internal
                    if existing_member.member_type == constants.UserMemberType.EXTERNAL:
                        is_external_user = True

                else:
                    member_to_be_deleted.append(member_id)

                # updating channel is_external column

                for channel_group in channels_groups:
                    if channel_group.group_id == member.parent_email and channel_group.is_external == False:
                        channel_group.is_external = is_external_user if is_external_user else False

                    # map - {key: group id, value: list[group/channel name, is_external]}
                    if channel_group.group_id not in channel_id_and_name_map:
                        channel_id_and_name_map[channel_group.group_id] = [channel_group.name, is_external_user]
                    elif channel_id_and_name_map[channel_group.group_id][1] == False and is_external_user:
                        channel_id_and_name_map[channel_group.group_id] = [channel_group.name, is_external_user]

            db_session.query(DirectoryStructure).filter(and_(DirectoryStructure.datasource_id == datasource_id,
                                                             DirectoryStructure.member_id.in_(member_to_be_deleted))).delete(
                synchronize_session='fetch'
            )

            # setting channel/group name in resource_permission table
            external_resource_ids = set()
            for permission in resource_permissions:
                if permission.email in channel_id_and_name_map:
                    is_external_exposure_type = channel_id_and_name_map[permission.email][1]
                    permission.email = channel_id_and_name_map[permission.email][0]
                    permission_exposure = permission.exposure_type
                    if is_external_exposure_type and permission_exposure != (constants.ResourceExposureType.ANYONEWITHLINK
                                              or constants.ResourceExposureType.PUBLIC):
                        permission.exposure_type = constants.ResourceExposureType.EXTERNAL
                        external_resource_ids.add(permission.resource_id)

            # updating resource exposure type for external
            db_session.query(Resource).filter(and_(Resource.datasource_id == datasource_id,
                                            Resource.resource_id.in_(external_resource_ids), Resource.exposure_type !=
                                                   (constants.ResourceExposureType.ANYONEWITHLINK or
                                                    constants.ResourceExposureType.PUBLIC))).update({Resource.exposure_type :
                                                                        constants.ResourceExposureType.EXTERNAL},synchronize_session='fetch')

            #update user_id with user_email in app association table
            db_session.query(ApplicationUserAssociation).filter(ApplicationUserAssociation.datasource_id == datasource_id,
                                                            DomainUser.datasource_id == datasource_id, DomainUser.user_id ==
                                                    ApplicationUserAssociation.user_email).\
                                        update({ApplicationUserAssociation.user_email : DomainUser.email},synchronize_session='fetch')


            try:
                db_connection().commit()
            except StaleDataError as sde:
                Logger().info("some other thread already proccessed the data : {}".format(sde.message))

            messaging.send_push_notification("adya-scan-update", json.dumps(datasource, cls=alchemy_encoder()))


def get_scan_status(datasource):
    # if datasource.file_scan_status > 10000 or datasource.user_scan_status > 1 or datasource.group_scan_status > 1:
    #     return 2 #Failed

    file_status = 1
    if (
                    datasource.file_scan_status >= file_status and datasource.total_file_count == datasource.processed_file_count) and (
                    datasource.user_scan_status == 1 and datasource.total_user_count == datasource.processed_user_count) and (
                    datasource.group_scan_status == 1 and datasource.total_group_count == datasource.processed_group_count):
        return 1  # Complete
    return 0  # In Progress
