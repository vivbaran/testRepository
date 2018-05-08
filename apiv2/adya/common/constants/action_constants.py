from enum import Enum


class ActionNames(Enum):
    TRANSFER_OWNERSHIP = "transfer_ownership"
    CHANGE_OWNER_OF_FILE = "change_owner"
    REMOVE_EXTERNAL_ACCESS = "remove_external_access"
    REMOVE_EXTERNAL_ACCESS_TO_RESOURCE = "remove_external_access_to_resource"
    MAKE_ALL_FILES_PRIVATE = "make_all_files_private"
    MAKE_RESOURCE_PRIVATE = "make_resource_private"
    DELETE_PERMISSION_FOR_USER = "delete_permission_for_user"
    UPDATE_PERMISSION_FOR_USER = "update_permission_for_user"
    WATCH_ALL_ACTION_FOR_USER = "watch_all_action_for_user"
    REMOVE_ALL_ACCESS_FOR_USER = "remove_all_access"
    REMOVE_USER_FROM_GROUP = "remove_user_from_group"
    ADD_USER_TO_GROUP = "add_user_to_group"
    ADD_PERMISSION_FOR_A_FILE = "add_permission_for_a_File"
    NOTIFY_USER_FOR_CLEANUP = "notify_user_for_clean_up"
    REMOVE_USER_FROM_APP = "remove_user_from_app"

class ActionStatus(Enum):
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'









