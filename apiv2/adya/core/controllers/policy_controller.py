import json
import uuid

from sqlalchemy import and_, or_

from adya.common.constants import constants
from adya.common.utils import messaging
from adya.common.utils.response_messages import ResponseMessage
from adya.core.controllers import domain_controller
from adya.gsuite import scan
from adya.common.db.connection import db_connection
from adya.common.db.models import Policy, LoginUser, PolicyCondition, PolicyAction, DataSource
from adya.common.db import db_utils


def get_policies(auth_token):
    db_session = db_connection().get_session()
    existing_user = db_utils.get_user_session(auth_token, db_session=db_session)
    user_domain_id = existing_user.domain_id
    is_admin = existing_user.is_admin
    is_service_account_is_enabled = existing_user.is_serviceaccount_enabled

    if is_service_account_is_enabled and is_admin:
        policies = db_session.query(Policy).filter(and_(DataSource.domain_id == user_domain_id,
                                                        Policy.datasource_id == DataSource.datasource_id)).all()

    else:
        policies = db_session.query(Policy).filter(and_(DataSource.domain_id == user_domain_id,
                                                        Policy.datasource_id == DataSource.datasource_id,
                                                        Policy.created_by == existing_user.email)).all()

    return policies


def delete_policy(policy_id):
    db_session = db_connection().get_session()
    existing_policy = db_session.query(Policy).filter(Policy.policy_id == policy_id).first()
    if existing_policy:
        db_session.query(PolicyAction).filter(PolicyAction.policy_id == policy_id).delete()
        db_session.query(PolicyCondition).filter(PolicyCondition.policy_id == policy_id).delete()

        db_session.delete(existing_policy)
        db_connection().commit()

        return existing_policy
    else:
        return ResponseMessage(400, "Bad Request - Policy not found")


def create_policy(auth_token, payload):
    db_session = db_connection().get_session()
    if payload:
        policy_id = str(uuid.uuid4())
        # inserting data into policy table
        policy = Policy()
        policy.policy_id = policy_id
        policy.datasource_id = payload["datasource_id"]
        policy.name = payload["name"]
        policy.description = payload["description"]
        policy.trigger_type = payload["trigger_type"]
        policy.created_by = payload["created_by"]
        db_session.add(policy)

        # inserting data into policy conditions table
        conditions = payload["conditions"]
        for condition in conditions:
            policy_condition = PolicyCondition()
            policy_condition.policy_id = policy_id
            policy_condition.datasource_id = payload["datasource_id"]
            policy_condition.match_type = condition["match_type"]
            policy_condition.match_condition = condition["match_condition"]
            policy_condition.match_value = condition["match_value"]
            db_session.add(policy_condition)

        # inserting data into policy actions table
        actions = payload["actions"]
        for action in actions:
            policy_action = PolicyAction()
            policy_action.policy_id = policy_id
            policy_action.datasource_id = payload["datasource_id"]
            policy_action.action_type = action["action_type"]
            policy_action.config = json.dumps(action["config"])
            db_session.add(policy_action)

        db_connection().commit()
        return policy

    return ResponseMessage(400, "Bad Request - Improper payload")


def update_policy(auth_token, policy_id, payload):
    delete_response = delete_policy(policy_id)
    if delete_response:
        policy = create_policy(auth_token, payload)
        return policy
    else:
        return ResponseMessage(400, "Bad Request - policy does not exist. update failed! ")
    

def validate(auth_token, datasource_id, resource_id, domain_id, payload):
    db_session = db_connection().get_session()
    old_permissions = payload["old_permissions"]
    old_permissions_map = {}
    for permission in old_permissions:
        old_permissions_map[permission.email] = permission

    resource = payload["resource"]
    new_permissions = resource["permissions"]
    for new_permission in new_permissions:
        if ((not new_permission.email in old_permissions_map)
            or (not old_permissions_map[new_permission.email].permission_type == new_permission.permission_type)):
            print "Permissions changed for this document, validate other policy conditions now..."
            policies = db_session.query(Policy).filter(and_(Policy.datasource_id == datasource_id,
                                                            Policy.trigger_type == constants.PolicyTriggerType.PERMISSION_CHANGE)).all()
            if not policies or len(policies) < 1:
                print "No policies found for permission change trigger, ignoring..."
                return

            for policy in policies:
                validate_resource_permission_change_policy(db_session, domain_id, policy, resource)
            return
    return


def validate_resource_permission_change_policy(db_session, domain_id, policy, resource):
    policy_conditions = policy.conditions
    datasource_id = policy.datasource_id
    response = False
    for policy_condition in policy_conditions:
        match_condition = policy_condition.match_condition
        match_value = policy_condition.match_value
        policy_match_type = policy_condition.match_type
        if policy_match_type == constants.PolicyMatchType.DOCUMENT_NAME:
            resource_name = resource['name']
            response = validate_permission_change_for_resource_name(match_condition, match_value, resource_name)

        elif policy_match_type == constants.PolicyMatchType.DOCUMENT_OWNER:
            resource_owner = resource['owners']
            response = validate_permission_change_for_resource_owner(match_condition, match_value, resource_owner)

        elif policy_match_type == constants.PolicyMatchType.DOCUMENT_EXPOSURE:
            response = validate_permission_change_for_resource_exposure(db_session, domain_id, datasource_id, match_condition, match_value, resource)

        elif policy_match_type == constants.PolicyMatchType.PERMISSION_EMAIL:
            resource_permissions = resource['permissions']
            response = validate_permission_change_for_permission_email(match_condition, match_value, resource_permissions)


    if response:
        policy_actions = db_session.query(PolicyAction).filter(PolicyCondition.policy_id == PolicyAction.policy_id).all()
        for action in policy_actions:
            if action == constants.policyActionType.SEND_EMAIL:
                print "send email"
                  # TODO: send email code

    else:
        print "no policy matched"
        return


def validate_permission_change_for_resource_name(match_condition, match_value, resource_name):
    print "match type is document name"
    response = match_condition_with_match_value(match_condition, match_value, resource_name)
    return response


def validate_permission_change_for_resource_owner(match_condition, match_value, resource_owner):
    print "match type is a document owner"
    response = match_condition_with_match_value(match_condition, match_value, resource_owner)
    return response


def validate_permission_change_for_resource_exposure(db_session, domain_id, datasource_id, match_condition, match_value, resource):
    print "macth type is document exposure"
    resource_permissions = resource['permissions']
    resource_exposure_type = constants.ResourceExposureType.PRIVATE
    for permission in resource_permissions:
        resource_exposure_type = scan.get_resources(db_session, domain_id, datasource_id, permission.email,
                                                    permission.displayName, resource_exposure_type)

    response = match_condition_with_match_value(match_condition, match_value, resource_exposure_type)
    return response


def validate_permission_change_for_permission_email(match_condition, match_value, resource_permissions):
    print "match type is permission email"
    perm_list = []
    for permission in resource_permissions:
        perm_list.append(permission.email)

    if (match_condition == constants.PolicyConditionMatch.EQUAL and match_value in perm_list) or \
            (match_condition == constants.PolicyConditionMatch.NOTEQUAL and match_value not in perm_list):
        return True
    elif match_condition == constants.PolicyConditionMatch.CONTAIN :
        for perm in perm_list:
            if match_value in perm:
                return True

    else:
        return False


# generic function for matching policy condition and corresponding value
def match_condition_with_match_value(match_condition, match_value, param):
    if (match_condition == constants.PolicyConditionMatch.EQUAL and match_value == param) or \
            (match_condition == constants.PolicyConditionMatch.NOTEQUAL and match_value != param):
            return True
    elif match_condition == constants.PolicyConditionMatch.CONTAIN and match_value in param:
        return True
    else:
        return False
