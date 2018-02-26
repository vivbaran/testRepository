import json
import datetime
import uuid

from flask import request

from adya.controllers import domain_controller
from adya.datasources.google import activities
from adya.db.models import LoginUser, DomainGroup, DomainUser, Resource, Report, ResourcePermission
from adya.db.connection import db_connection
from adya.common import utils, constants, request_session
from sqlalchemy import func, or_, and_


def get_widget_data(auth_token, widget_id):
    if not auth_token:
        return None
    db_session = db_connection().get_session()
    data = None
    if widget_id == 'usersCount':
        data = db_session.query(DomainUser).filter(DomainUser.domain_id == LoginUser.domain_id).filter(
            LoginUser.auth_token == auth_token).count()
    elif widget_id == 'groupsCount':
        data = db_session.query(DomainGroup).filter(DomainGroup.domain_id == LoginUser.domain_id).filter(
            LoginUser.auth_token == auth_token).count()
    elif widget_id == 'filesCount':
        data = db_session.query(Resource).filter(
            and_(Resource.domain_id == LoginUser.domain_id, Resource.resource_type != 'folder')).filter(
            LoginUser.auth_token == auth_token).count()
    elif widget_id == 'foldersCount':
        data = db_session.query(Resource).filter(
            and_(Resource.domain_id == LoginUser.domain_id, Resource.resource_type == 'folder')).filter(
            LoginUser.auth_token == auth_token).count()
    elif widget_id == 'sharedDocsByType':
        data = db_session.query(Resource.exposure_type, func.count(Resource.exposure_type)).filter(
            Resource.exposure_type != constants.ResourceExposureType.INTERNAL).group_by(
            Resource.exposure_type).all()
    elif widget_id == 'sharedDocsList':
        data = {}
        data["rows"] = db_session.query(Resource.resource_name, Resource.resource_type).filter(
            and_(Resource.domain_id == LoginUser.domain_id,
                 or_(Resource.exposure_type == constants.ResourceExposureType.EXTERNAL,
                     Resource.exposure_type == constants.ResourceExposureType.PUBLIC))).filter(
            LoginUser.auth_token == auth_token).limit(5).all()
        data["totalCount"] = db_session.query(Resource.resource_name, Resource.resource_type).filter(
            and_(Resource.domain_id == LoginUser.domain_id,
                 or_(Resource.exposure_type == constants.ResourceExposureType.EXTERNAL,
                     Resource.exposure_type == constants.ResourceExposureType.PUBLIC))).filter(
            LoginUser.auth_token == auth_token).count()
    elif widget_id == 'externalUsersList':
        data = {}
        data["rows"] = db_session.query(DomainUser.email, func.count(ResourcePermission.email)).filter(and_(DomainUser.domain_id == LoginUser.domain_id,
                                                                      DomainUser.member_type == constants.UserMemberType.EXTERNAL,
                                                            ResourcePermission.domain_id == LoginUser.domain_id ,
                                                            ResourcePermission.email == DomainUser.email)).filter(
            LoginUser.auth_token == auth_token).group_by(DomainUser.email).order_by(func.count(ResourcePermission.email).desc()).limit(5).all()
        data["totalCount"] = db_session.query(DomainUser.email).filter(and_(DomainUser.domain_id == LoginUser.domain_id,
                                                                            DomainUser.member_type == constants.UserMemberType.EXTERNAL)).filter(
            LoginUser.auth_token == auth_token).count()
    return data


def create_report(auth_token, payload):
    db_session = db_connection().get_session()
    report_id = str(uuid.uuid4())

    existing_user = db_session.query(LoginUser).filter(LoginUser.auth_token == auth_token).first()
    if existing_user:
        report = Report()
        report.domain_id = existing_user.domain_id
        report.report_id = report_id
        creation_time = datetime.datetime.utcnow().isoformat()
        if payload:
            report.name = payload["name"]
            if 'description' in payload:
                report.description = payload["description"]

            report.frequency = payload["frequency"]
            report.receivers = payload["receivers"]
            config_input = {"report_type": payload["report_type"],
                            "selected_entity_type": payload["selected_entity_type"],
                            "selected_entity": payload["selected_entity"], "selected_entity_name": payload["selected_entity_name"]}

            report.config = json.dumps(config_input)
            report.is_active = payload["is_active"]

        report.creation_time = creation_time

        db_session.add(report)
        try:
            db_session.commit()
        except Exception as ex:
            print (ex)

        return report
    else:
        return None


def get_reports(auth_token):
    if not auth_token:
        return None
    db_session = db_connection().get_session()
    reports_data = db_session.query(Report).filter(Report.domain_id == LoginUser.domain_id).filter(
        LoginUser.auth_token ==
        auth_token).all()

    response = {}
    for report in reports_data:
        config_data = json.loads(report.config)
        last_trigger_time = ''
        if report.last_trigger_time: last_trigger_time = report.last_trigger_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        response[report.report_id] = {
            "report_id": report.report_id,
            "name": report.name,
            "description": report.description,
            "frequency": report.frequency[5:len(report.frequency) - 1],
            "receivers": report.receivers,
            "creation_time": report.creation_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_trigger_time": last_trigger_time,
            "is_active": str(report.is_active),
            "report_type": config_data['report_type'],
            "selected_entity": config_data['selected_entity'],
            "selected_entity_type": config_data['selected_entity_type'],
            "selected_entity_name": config_data['selected_entity_name']

        }
    return response


def delete_report(auth_token, report_id):
    if not auth_token:
        return None
    db_session = db_connection().get_session()
    existing_report = db_session.query(Report).filter(Report.report_id == report_id).first()
    db_session.delete(existing_report)
    try:
        db_session.commit()
    except:
        print "Exception occured while delete a report"

    return existing_report


def run_report(domain_id, datasource_id, auth_token, report_id):
    if not auth_token:
        return None
    session = db_connection().get_session()

    get_report_info = session.query(Report.config, Report.receivers, Report.last_trigger_time, Report.description).filter(
        and_(Report.domain_id == LoginUser.domain_id,
             Report.report_id == report_id)). \
        filter(LoginUser.auth_token == auth_token).one()

    config_data = json.loads(get_report_info[0])
    email_list = get_report_info[1]
    last_run_time = get_report_info[2]
    report_desc = get_report_info[3]

    report_type = config_data.get('report_type')
    selected_entity = config_data.get('selected_entity')
    selected_entity_type = config_data.get('selected_entity_type')
    response_data = []
    if report_type == "Permission":
        if selected_entity_type == "group":
            query_string = ResourcePermission.email == selected_entity
        elif selected_entity_type == "resource":
            query_string = ResourcePermission.resource_id == selected_entity

        get_perms_report = session.query(ResourcePermission, Resource).filter(and_(ResourcePermission.domain_id ==
                                                                                   LoginUser.domain_id, query_string,
                                                                                   Resource.resource_id
                                                                                   == ResourcePermission.resource_id)). \
            filter(LoginUser.auth_token
                   == auth_token).all()

        for perm_Report in get_perms_report:
            data_map = {
                "resource_name": perm_Report.Resource.resource_name,
                "resource_type": perm_Report.Resource.resource_type,
                "resource_size": perm_Report.Resource.resource_size,
                "resource_owner_id": perm_Report.Resource.resource_owner_id,
                "last_modified_time": str(perm_Report.Resource.last_modified_time),
                "creation_time": str(perm_Report.Resource.creation_time),
                "exposure_type": perm_Report.Resource.exposure_type,
                "user_email": perm_Report.ResourcePermission.email,
                "permission_type": perm_Report.ResourcePermission.permission_type
            }

            response_data.append(data_map)

    elif report_type == "Activity":
        if selected_entity_type == "group":
            get_activity_report = activities.get_activities_for_user(domain_id, datasource_id, selected_entity,
                                                                     last_run_time)
            for datalist in get_activity_report:
                data_map = {
                    "date": datalist[0],
                    "operation": datalist[1],
                    "datasource": datalist[2],
                    "resource": datalist[3],
                    "type": datalist[4],
                    "ip_address": datalist[5]

                }

                response_data.append(data_map)

    return response_data, email_list, report_type, report_desc


def update_report(auth_token, payload):
    if not auth_token:
        return None
    session = db_connection().get_session()
    if payload:
        report_id = payload['report_id']
        session.query(Report).filter(Report.report_id == report_id).update(payload)
        try:
            session.commit()
        except Exception as ex:
            print ex
        return "successful update "
    else:
        return None


def generate_csv_report(auth_token, report_id):
    data_source = domain_controller.get_datasource(auth_token, None)

    domain_id = data_source[0].domain_id
    datasource_id = data_source[0].datasource_id

    report_data, email_list, report_type, report_desc = run_report(domain_id, datasource_id, auth_token, report_id)
    csv_records = ""

    if report_type == "Permission":

        perm_csv_display_header = ["File Name", "File Type", "Size", "Owner", "Last Modified Date", "Creation Date",
                           "File Exposure", "User Email", "Permission"]

        perm_report_data_header = ["resource_type", "resource_name", "resource_size", "resource_owner_id",
                                   "last_modified_time", "creation_time",
                                   "exposure_type", "user_email", "permission_type"]

        csv_records += ",".join(perm_csv_display_header) + "\n"
        for data in report_data:
            for header in perm_report_data_header:
                csv_records += ",".join(data[header])
            csv_records += "\n"

    elif report_type == "Activity":

        activity_csv_display_header = ["Date", "Operation", "Datasource", "Resource", "Type", "IP Address"]

        activity_report_data_header = ["date", "operation", "datasource", "resource", "type", "ip_address"]

        csv_records += ",".join(activity_csv_display_header) + "\n"
        for data in report_data:
            for header in activity_report_data_header:
                csv_records += ",".join(data[header])
            csv_records += "\n"

    return csv_records, email_list, report_desc
