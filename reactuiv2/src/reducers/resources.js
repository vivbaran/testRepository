import {
    RESOURCES_PAGE_LOADED,
    RESOURCES_PAGE_LOAD_START,
    RESOURCES_TREE_SET_ROW_DATA,
    RESOURCES_ACTION_LOAD,
    RESOURCES_ACTION_CANCEL,
    RESOURCES_FILTER_CHANGE,
    RESOURCES_SEARCH_PAYLOAD,
    RESOURCES_SEARCH_EMPTY,
    RESOURCES_PAGINATION_DATA,
    LOGOUT
} from '../constants/actionTypes';

const defaultState = {
    isLoading: false,
    filterExposureType: 'EXT',
    filterResourceName: '',
    filterResourceType: '',
    filterEmailId: '',
    filterParentFolder: '',
    filterByDate: '',
    pageNumber: 0,
    pageLimit: 100
};

export default (state = defaultState, action) => {
    switch (action.type) {
        case RESOURCES_PAGE_LOAD_START:
            return {
                ...state,
                isLoading: true
            }
        case RESOURCES_PAGE_LOADED:
            // if (action.parent) {
            //     var keys = Object.keys(action.payload)
            //     if (keys.length > 0) {
            //         var children = [];
            //         for (let index = 0; index < keys.length; index++) {
            //             let child = action.payload[keys[index]]
            //             child.isExpanded = false;
            //             child.key = keys[index];
            //             child.depth = action.parent.depth + 1;
            //             if (!child.name)
            //                 child.name = child.resourceName
            //             children.push(child)
            //         }
            //         action.parent['isExpanded'] = true;
            //         action.parent['children'] = children;
            //     }
            //     else {
            //         action.parent['isExpanded'] = false
            //         action.parent['children'] = []
            //     }
            // }
            // else {
            //     var rows = [];
            //     if (action.payload) {
            //         var keys = Object.keys(action.payload)

            //         for (let index = 0; index < keys.length; index++) {
            //             let row = action.payload[keys[index]]
            //             row.isExpanded = row.isExpanded || false;
            //             row.key = keys[index];
            //             row.depth = 0;
            //             if (!row.name)
            //                 row.name = row.resourceName
            //             rows.push(row)
            //         }
            //     }
            //     state.resourceTree = rows;
            // }
            // return {
            //     ...state,
            //     isLoading: false,
            //     cellExpanded: false,
            //     rowData: {}
            // }

            // console.log("resources payload : ", action.payload)
            // let keys = Object.keys(action.payload)
            // let rows = []

            // for (let index=0; index<keys.length; index++) {
            //     var row = action.payload[keys[index]];
            //     var parent = ""
            //     if(row.parents)
            //     {
            //         parent = row.parents.parentName;
            //     }

            //     row.parent = parent;
            //     rows.push(row)
            // }
            return {
                ...state,
                isLoading: false,
                resourceTree: !action.error ? action.payload : []
            }
        case RESOURCES_PAGINATION_DATA:
            return {
                ...state,
                pageNumber: action.pageNumber,
                pageLimit: action.pageLimit
            }
        case RESOURCES_SEARCH_PAYLOAD:
            return {
                ...state,
                resourceSearchPayload: action.payload
            }
        case RESOURCES_SEARCH_EMPTY:
            return {
                ...state,
                resourceSearchPayload: undefined
            }
        case RESOURCES_TREE_SET_ROW_DATA:
            return {
                ...state,
                rowData: action.payload
            }
        case RESOURCES_ACTION_LOAD:
            return {
                ...state,
                action: {
                    key: action.actionType,
                    resource_id: state.rowData.resource_id,
                    resource_name: state.rowData.resource_name,
                    old_owner_email: state.rowData.resource_owner_id,
                    resource_owner_id: state.rowData.resource_owner_id,
                    new_permission_role: action.newValue,
                    user_email: action.permission ? action.permission.email : undefined,
                    user_type: action.permission ? action.permission.type: undefined
                }
            }
        case RESOURCES_ACTION_CANCEL:
            return {
                ...state,
                action: undefined
            }
        case RESOURCES_FILTER_CHANGE:
            state[action.property] = action.value
            return {
                ...state,
                isLoading: true
            }
        case LOGOUT:
            return {
                ...state,
                resourceTree: undefined,
                resourceSearchPayload: undefined
            }

        // case RESOURCES_TREE_CELL_EXPANDED:
        //     return {
        //         ...state,
        //         cellExpanded: action.payload
        //     }
        default:
            return state;
    }
};
