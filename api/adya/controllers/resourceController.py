from adya.db.connection import db_connection
from adya.db.models import Resource,ResourcePermission,LoginUser,DataSource,ResourcePermission,ResourceParent,Domain
from sqlalchemy import and_, desc
from sqlalchemy.orm import aliased
import json
from adya.common import utils
from sets import Set

# def get_resource_tree(auth_token, parent_id,emailList=None):
#     if not auth_token:
#         return None
#     db_session = db_connection().get_session()
#     domain_id,datasource_id_list_data = utils.get_domain_id_and_datasource_id_list(db_session,auth_token)
#     resources_tree ={}
#     resources = []
#     for datasource in datasource_id_list_data:
#         datasource_id = datasource.datasource_id

#         if emailList:
#             resource_permissions_query_data=None
#             if not parent_id:
#                 resource_permissions_query_data = db_session.query(Resource,ResourcePermission).outerjoin(ResourcePermission,
#                                         and_(ResourcePermission.resource_id == Resource.resource_id,
#                                         ResourcePermission.domain_id == Resource.domain_id)).filter(and_(Resource.domain_id == domain_id,
#                                         Resource.resource_type =='folder',
#                                         ResourcePermission.email.in_(emailList))).all()
#             else:
#                 resource_permissions_query_data = db_session.query(Resource,ResourcePermission).outerjoin(ResourcePermission,
#                                         and_(ResourcePermission.resource_id == Resource.resource_id,
#                                         ResourcePermission.domain_id == Resource.domain_id)).filter(and_(Resource.domain_id == domain_id,
#                                         ResourcePermission.email.in_(emailList),Resource.resource_parent_id == parent_id)).all()
#             resource_id_set = Set()
#             for row in resource_permissions_query_data:
#                 resource_id_set.add(row.Resource.resource_id)
#             resource_data =[]
#             for row in resource_permissions_query_data:
#                 if (row.Resource.resource_parent_id != None and not row.Resource.resource_parent_id in resource_id_set) \
#                     or row.Resource.resource_parent_id == None :
#                     resources.append(row)
#         else:
#             if not parent_id:
#                 resources = db_session.query(Resource,ResourcePermission).outerjoin(ResourcePermission,
#                                     and_(ResourcePermission.resource_id == Resource.resource_id,
#                                     ResourcePermission.domain_id == Resource.domain_id)).filter(and_(Resource.domain_id == domain_id,
#                                     Resource.resource_type =='folder',Resource.resource_parent_id == parent_id)).all()
#             else:
#                 resources = db_session.query(Resource,ResourcePermission).outerjoin(ResourcePermission,
#                                     and_(ResourcePermission.resource_id == Resource.resource_id,
#                                     ResourcePermission.domain_id == Resource.domain_id)).filter(and_(Resource.domain_id == domain_id,
#                                     Resource.resource_parent_id == parent_id)).all()

#     responsedata ={}
#     for resource in resources:
#         if resource.ResourcePermission:
#             permissionobject = {
#                                     "permissionId":resource.ResourcePermission.permission_id,
#                                     "pemrissionEmail":resource.ResourcePermission.email,
#                                     "permissionType":resource.ResourcePermission.permission_type
#                             }
#         else:
#             permissionobject ={}

#         if not resource.Resource.resource_id in responsedata:
#             responsedata[resource.Resource.resource_id] = {
#                 "resourceId":resource.Resource.resource_id,
#                 "resourceName":resource.Resource.resource_name,
#                 "resourceType":resource.Resource.resource_type,
#                 "resourceOwnerId":resource.Resource.resource_owner_id,
#                 "exposureType":resource.Resource.exposure_type,
#                 "permissions":[permissionobject]
#             }
#         else:
#             responsedata[resource.Resource.resource_id]["permissions"].append(permissionobject)
#     resources_tree[datasource_id] = responsedata
#     return responsedata


def get_resources(auth_token, user_emails=None, exposure_type='EXT', resource_type='None', prefix=''):
    if not auth_token:
        return None
    db_session = db_connection().get_session()
    domain = db_session.query(Domain).filter(LoginUser.domain_id == Domain.domain_id). \
        filter(LoginUser.auth_token == auth_token).first()
    limit = 100
    resources = []
    resource_alias = aliased(Resource)
    parent_alias = aliased(Resource)
    resources_query = db_session.query(resource_alias, parent_alias.resource_name).outerjoin(parent_alias, resource_alias.parent_id == parent_alias.resource_id)
    if user_emails:
        resource_ids = db_session.query(ResourcePermission.resource_id).filter(and_(ResourcePermission.domain_id == domain.domain_id, ResourcePermission.email.in_(user_emails)))
        resources_query = resources_query.filter(resource_alias.resource_id.in_(resource_ids))
    else:
        resources_query = resources_query.join("permissions")
    if resource_type:
        resources_query = resources_query.filter(resource_alias.resource_type == resource_type)
    if exposure_type:
        resources_query = resources_query.filter(resource_alias.exposure_type == exposure_type)
    if prefix:
        limit = 10
        resources_query = resources_query.filter(resource_alias.resource_name.ilike("%" + prefix + "%"))

    resources = resources_query.filter(resource_alias.domain_id == domain.domain_id).order_by(desc(resource_alias.last_modified_time)).limit(limit).all()
    result = []
    for resource in resources:
        resource[0].parent_name = resource.resource_name
        result.append(resource[0])
    return result

def search_resources(auth_token, prefix):
    if not auth_token:
        return None
    if not prefix:
        return []
    db_session = db_connection().get_session()
    resources = db_session.query(Resource).filter(and_(Resource.domain_id == LoginUser.domain_id, Resource.resource_name.ilike("%" + prefix + "%"))).filter(LoginUser.auth_token == auth_token).limit(10).all()

    return resources
