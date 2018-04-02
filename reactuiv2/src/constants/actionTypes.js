export const APP_LOAD = 'APP_LOAD';
export const REDIRECT = 'REDIRECT';

export const DASHBOARD_PAGE_LOADED = 'DASHBOARD_PAGE_LOADED';
export const DASHBOARD_PAGE_UNLOADED = 'DASHBOARD_PAGE_UNLOADED';

export const DASHBOARD_WIDGET_LOAD_START = 'DASHBOARD_WIDGET_LOAD_START';
export const DASHBOARD_WIDGET_LOADED = 'DASHBOARD_WIDGET_LOADED';
export const DASHBOARD_REDIRECT_TO_PARAM = 'DASHBOARD_REDIRECT_TO_PARAM'

export const USERS_PAGE_LOADED = 'USERS_PAGE_LOADED';
export const USERS_PAGE_UNLOADED = 'USERS_PAGE_UNLOADED';
export const USERS_PAGE_LOAD_START = 'USERS_TREE_LOAD_START';


export const APP_USERS_LOAD_START = 'APP_USERS_LOAD_START';
export const APP_USERS_LOADED = 'APP_USERS_LOADED';

export const USER_APPS_LOAD_START = 'USER_APPS_LOAD_START';
export const USER_APPS_LOADED = 'USER_APPS_LOADED';

export const APPS_ITEM_SELECTED = 'APPS_ITEM_SELECTED';
export const APPS_PAGE_LOADED = 'APPS_PAGE_LOADED';
export const APPS_PAGE_UNLOADED = 'APPS_PAGE_UNLOADED';
export const APPS_PAGE_LOAD_START = 'APPS_PAGE_LOAD_START';

export const USER_ITEM_SELECTED = 'USER_ITEM_SELECTED';

export const USERS_ACTIVITY_LOAD_START = 'USERS_ACTIVITY_LOAD_START';
export const USERS_ACTIVITY_LOADED = 'USERS_ACTIVITY_LOADED';

export const USERS_RESOURCE_LOAD_START = 'USERS_RESOURCE_LOAD_START';
export const USERS_RESOURCE_LOADED = 'USERS_RESOURCE_LOADED';
export const USERS_RESOURCE_ACTION_LOAD = 'USERS_RESOURCE_ACTION_LOAD';
export const USERS_RESOURCE_ACTION_CANCEL = 'USERS_RESOURCE_ACTION_CANCEL';
export const USERS_RESOURCE_SET_FILE_SHARE_TYPE = 'USERS_RESOURCE_SET_FILE_SHARE_TYPE';
export const USERS_OWNED_RESOURCES_LOAD_START = 'USERS_OWNED_RESOURCES_LOAD_START'
export const USERS_OWNED_RESOURCES_LOADED = 'USERS_OWNED_RESOURCES_LOADED'
export const USERS_RESOURCE_PAGINATION_DATA = 'USERS_RESOURCE_PAGINATION_DATA'
export const USERS_RESOURCE_FILTER_CHANGE = 'USERS_RESOURCE_FILTER_CHANGE'


export const RESOURCES_PAGE_LOAD_START = 'RESOURCES_PAGE_LOAD_START';
export const RESOURCES_PAGE_LOADED = 'RESOURCES_PAGE_LOADED';
export const RESOURCES_PAGE_UNLOADED = 'RESOURCES_PAGE_UNLOADED';
export const RESOURCES_TREE_SET_ROW_DATA = 'RESOURCES_TREE_SET_ROW_DATA';
export const RESOURCES_TREE_CELL_EXPANDED = 'RESOURCES_TREE_CELL_EXPANDED';
export const RESOURCES_ACTION_LOAD = 'RESOURCES_ACTION_LOAD';
export const RESOURCES_ACTION_CANCEL = 'RESOURCES_ACTION_CANCEL';
export const RESOURCES_FILTER_CHANGE = 'RESOURCES_FILTER_CHANGE';
export const RESOURCES_PAGINATION_DATA = 'RESOURCES_PAGINATION_DATA';

// export const REPORTS_PAGE_LOADED = 'REPORTS_PAGE_LOADED';
// export const REPORTS_PAGE_UNLOADED = 'REPORTS_PAGE_UNLOADED';

export const GROUP_SEARCH_PAYLOAD = 'GROUP_SEARCH_PAYLOAD';
export const GROUP_SEARCH_EMPTY = 'GROUP_SEARCH_EMPTY';

export const RESOURCES_SEARCH_PAYLOAD = 'RESOURCES_SEARCH_PAYLOAD';
export const RESOURCES_SEARCH_EMPTY = 'RESOURCES_SEARCH_EMPTY';

export const APPS_SEARCH_PAYLOAD = 'APPS_SEARCH_PAYLOAD';

export const SET_CURRENT_URL = 'SET_CURRENT_URL';

export const LOGIN = 'LOGIN';
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
export const LOGIN_ERROR = 'LOGIN_ERROR';
export const LOGOUT = 'LOGOUT';
export const LOGIN_START = 'LOGIN_START';

export const GET_ALL_ACTIONS = 'GET_ALL_ACTIONS'

export const LOGIN_PAGE_UNLOADED = 'LOGIN_PAGE_UNLOADED';

export const ASYNC_START = 'ASYNC_START';
export const ASYNC_END = 'ASYNC_END';

export const AUDIT_LOG_LOAD_START = 'AUDIT_LOG_LOAD_START';
export const AUDIT_LOG_LOADED = 'AUDIT_LOG_LOADED';

export const SET_DATASOURCES = 'SET_DATASOURCES';
export const CREATE_DATASOURCE = 'CREATE_DATASOURCE';
export const DATASOURCE_LOAD_START = 'DATASOURCE_LOAD_START';
export const DATASOURCE_LOAD_END = 'DATASOURCE_LOAD_END';
export const DELETE_DATASOURCE_START = 'DELETE_DATASOURCE';
export const SCAN_UPDATE_RECEIVED = 'SCAN_UPDATE_RECEIVED';
export const SCAN_INCREMENTAL_UPDATE_RECEIVED = 'SCAN_INCREMENTAL_UPDATE_RECEIVED';

export const REPORTS_CRON_EXP = 'REPORTS_CRON_EXP';
export const CREATE_SCHEDULED_REPORT = 'CREATE_SCHEDULED_REPORT';
export const SET_SCHEDULED_REPORTS = 'SET_SCHEDULED_REPORTS';
export const DELETE_SCHEDULED_REPORT = 'DELETE_SCHEDULED_REPORT';
export const RUN_SCHEDULED_REPORT = 'RUN_SCHEDULED_REPORT';
export const DELETE_OLD_SCHEDULED_REPORT = 'DELETE_OLD_SCHEDULED_REPORT';
export const UPDATE_SCHEDULED_REPORT= 'UPDATE_SCHEDULED_REPORT';
export const REPORTS_PAGE_LOADING = 'REPORTS_PAGE_LOADING'

export const SET_POLICY_ROW_FILTERS = 'SET_POLICY_ROW_FILTERS'
export const SET_POLICY_FILTER = 'SET_POLICY_FILTER'
export const CREATE_POLICY_LOAD_START = 'CREATE_POLICY_LOAD_START'
export const CREATE_POLICY_LOADED = 'CREATE_POLICY_LOADED'

export const API_ROOT = process.env.REACT_APP_API_ROOT || 'http://127.0.0.1:5000';
export const FLAG_ERROR_MESSAGE = 'FLAG_ERROR_MESSAGE';
export const CLEAR_MESSAGE = 'CLEAR_MESSAGE';
export const USERS_GROUP_ACTION_LOAD = 'USERS_GROUP_ACTION_LOAD';
