import React, {Component} from 'react';
import {Tab,Segment,Sticky,Icon} from 'semantic-ui-react';
import {connect} from 'react-redux';
import ResourcePermissions from './ResourcePermissions';
import ResourceDetails from './ResourceDetails';
import {RESOURCES_TREE_SET_ROW_DATA, RESOURCES_ACTION_LOAD} from '../../constants/actionTypes';

const mapStateToProps = state => ({
    ...state.resources
})

const mapDispatchToProps = dispatch => ({
    closingDetailsSection: (payload) => dispatch({ type:RESOURCES_TREE_SET_ROW_DATA, payload }),
    onChangePermissionForResource: (actionType, resource, newValue, email) =>
        dispatch({ type: RESOURCES_ACTION_LOAD, actionType, resource, newValue, email })
})

class ResourcePermissionSection extends Component {
    constructor(props) {
        super(props);
        this.state = {
            rowData: '',
            "Transfer ownership": "change_owner",
            "Remove external access": "remove_external_access_to_resource",
            "Remove write access": "removeWriteAccess",
            "Make this private": "make_resource_private",
            "Watch all actions": "watchAllActions"
        }
        this.closeDetailsSection = this.closeDetailsSection.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleClick = this.handleClick.bind(this);
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.rowData) {
            this.setState({
                rowData: nextProps.rowData
            })
        }
    }

    closeDetailsSection() {
        this.props.closingDetailsSection(undefined)
    }

    handleChange(event,data,email) {
        if (data["value"] !== "Read" && data["value"] !== "Write") {
            this.props.onChangePermissionForResource(this.state[data["value"]],data,data["value"],email)
        }
        else {
            this.props.onChangePermissionForResource('update_permission_for_user',data,data["value"],email)
        }
    }

    handleClick(event,userEmail,permissionType) {
        this.props.onChangePermissionForResource('delete_permission_for_user',permissionType,undefined,userEmail)
    }

    render() {
        let panes = [
            { menuItem: 'Permissions', render: () => <Tab.Pane attached={false}><ResourcePermissions rowData={this.state.rowData} handleChange={this.handleChange} handleClick={this.handleClick}/></Tab.Pane> }
          ]
        return (
            <Segment>
                {/* <Sticky> */}
                    <Icon name='close' onClick={this.closeDetailsSection} />
                    <ResourceDetails rowData={this.props.rowData} handleChange={this.handleChange} />
                    <Tab menu={{ secondary: true, pointing: true }} panes={panes} />
                {/* </Sticky> */}
            </Segment>
        )
    }
}

export default connect(mapStateToProps,mapDispatchToProps)(ResourcePermissionSection);
