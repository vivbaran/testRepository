
import auth from './reducers/auth';
import { combineReducers } from 'redux';
import common from './reducers/common';
import dashboard from './reducers/dashboard';

export default combineReducers({
  auth,
  common,
  dashboard
});