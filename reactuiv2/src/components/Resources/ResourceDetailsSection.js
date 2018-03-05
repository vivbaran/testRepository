import React, { Component } from 'react';
import { Tab, Segment, Icon } from 'semantic-ui-react';
import { connect } from 'react-redux';
import ResourcePermissions from './ResourcePermissions';
import ResourceDetails from './ResourceDetails';
import { RESOURCES_TREE_SET_ROW_DATA, RESOURCES_ACTION_LOAD } from '../../constants/actionTypes';

const mapStateToProps = state => ({
    ...state.resources
})

const mapDispatchToProps = dispatch => ({
    closingDetailsSection: (payload) => dispatch({ type: RESOURCES_TREE_SET_ROW_DATA, payload }),
    onChangePermissionForResource: (actionType, permission, newValue) =>
        dispatch({ type: RESOURCES_ACTION_LOAD, actionType, permission, newValue }),
    onResourceQuickAction: (actionType) =>
        dispatch({ type: RESOURCES_ACTION_LOAD, actionType })
})

class ResourceDetailsSection extends Component {
    constructor(props) {
        super(props);
        this.closeDetailsSection = this.closeDetailsSection.bind(this);
        this.onPermissionChange = this.onPermissionChange.bind(this);
        this.onQuickAction = this.onQuickAction.bind(this);
        this.onRemovePermission = this.onRemovePermission.bind(this);
    }

    closeDetailsSection() {
        this.props.closingDetailsSection(undefined)
    }

    onPermissionChange(event, permission, newValue) {
        if (permission.permission_type !== newValue)
            this.props.onChangePermissionForResource('update_permission_for_user', permission, newValue)
    }

    onQuickAction(action) {
        if (action !== '')
            this.props.onChangePermissionForResource(action)
    }

    onRemovePermission(event, permission) {
        this.props.onChangePermissionForResource('delete_permission_for_user', permission, "")
    }

    render() {
        let panes = [
            { menuItem: 'Permissions', render: () => <Tab.Pane attached={false}><ResourcePermissions rowData={this.props.rowData} onPermissionChange={this.onPermissionChange} onRemovePermission={this.onRemovePermission} /></Tab.Pane> }
        ]
        return (
            <Segment>
                {/* <Sticky> */}
                <Icon name='close' onClick={this.closeDetailsSection} />
                <ResourceDetails rowData={this.props.rowData} onQuickAction={this.onQuickAction} />
                <Tab menu={{ secondary: true, pointing: true }} panes={panes} rowData={this.props.rowData} />
                {/* </Sticky> */}
            </Segment>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ResourceDetailsSection);
