import {
    DASHBOARD_PAGE_LOADED,
    DASHBOARD_WIDGET_LOADED,
    DASHBOARD_WIDGET_LOAD_START,
    LOGOUT
} from '../constants/actionTypes';

const defaultState = {
  };

export default (state = defaultState, action) => {
    switch (action.type) {
        case DASHBOARD_PAGE_LOADED:
            return state;
        case DASHBOARD_WIDGET_LOAD_START:
            state[action.widgetId] = {isLoaded: false};
            return {
                ...state
            }
        case DASHBOARD_WIDGET_LOADED:
            let errorPayload
            if (action.widgetId.includes("Count"))
                errorPayload = 0
            else 
                errorPayload = {totalCount:0, rows: []}
            state[action.widgetId] = {isLoaded: true, data: !action.error?action.payload:errorPayload};
            return {
                ...state
            }
        case LOGOUT:
            return {
                ...defaultState
            }
        default:
            return state;
    }
};