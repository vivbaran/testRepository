import React, { Component } from 'react';

import agent from '../../utils/agent'
import ResourceCell from '../Resources/ResourceCell';
import { Loader, Dimmer } from 'semantic-ui-react'

import { connect } from 'react-redux';

import { AgGridReact } from "ag-grid-react";
import 'ag-grid/dist/styles/ag-grid.css';
import 'ag-grid/dist/styles/ag-theme-fresh.css';

import {
    USERS_RESOURCE_LOAD_START,
    USERS_RESOURCE_LOADED,
    USERS_RESOURCE_ACTION_LOAD,
    API_ERROR
} from '../../constants/actionTypes';


const mapStateToProps = state => ({
    ...state.users,
    ...state.common
});

const mapDispatchToProps = dispatch => ({
    onLoadStart: (payload) =>
        dispatch({ type: USERS_RESOURCE_LOAD_START, payload }),
    onLoad: (payload) =>
        dispatch({ type: USERS_RESOURCE_LOADED, payload }),
    onChangePermission: (actionType, resource, newValue) =>
        dispatch({ type: USERS_RESOURCE_ACTION_LOAD, actionType, resource, newValue }),
    onLoadError: (errors) => 
        dispatch({ type: API_ERROR, errors })
});

class UserResource extends Component {
    constructor(props) {
        super(props);

        this.cellValueChanged = this.cellValueChanged.bind(this);
        this.state = {
            columnDefs: [
                {
                    headerName: "Resource",
                    field: "name"
                },
                {
                    headerName: "Owner",
                    field: "resourceOwnerId",
                    editable: true,
                    onCellValueChanged: this.cellValueChanged
                },
                {
                    headerName: "My permission",
                    field: "myPermission",
                    editable: true,
                    cellEditor: "agSelectCellEditor",
                    cellEditorParams: {
                        values: ['Read','Write','None']
                    },
                    onCellValueChanged: this.cellValueChanged,
                    cellStyle: {"textAlign":"center"}
                },
                {
                    headerName: "ExposureType",
                    field: "exposureType"
                }
            ],
            getNodeChildDetails: function getNodeChildDetails(rowItem) {
                if (rowItem.resourceType == 'folder') {
                    return {
                        group: true,
                        expanded: rowItem.isExpanded,
                        children: rowItem.children || [],
                        key: rowItem.key
                    }
                }
                return null;
            },
            exposureType: undefined
        };
    }

    cellValueChanged(params) {
        console.log("Cell column value changed: ", params)
        if (['Read','Write','None'].indexOf(params.newValue) !== -1)
            this.props.onChangePermission("resourcePermissionChange", params.data, params.newValue);
        else
            this.props.onChangePermission("resourceOwnerPermissionChange", params.data, params.oldValue)
    }

    componentWillReceiveProps(nextProps) {
        if (this.props.selectedUserItem["key"] != nextProps.selectedUserItem["key"] && !nextProps.selectedUserItem.resources) {
            nextProps.onLoadStart(nextProps.selectedUserItem["key"])
            //nextProps.onLoad(agent.Resources.getResourcesTree({'userEmails': [nextProps.selectedUserItem["key"]], 'exposureType': nextProps.exposureType?nextProps.exposureType:'EXT'}))
            let getResourcesTree = agent.Resources.getResourcesTree({'userEmails': [nextProps.selectedUserItem["key"]], 'exposureType': nextProps.exposureType?nextProps.exposureType:'EXT'})
            
            if (getResourcesTree['statusCode'] !== 200) {
                console.log("getResourcesTree['statusText']: ", getResourcesTree['statusText'])
                this.props.onLoadError(getResourcesTree['statusText'])
            }
            else 
                nextProps.onLoad(getResourcesTree)
        }
        if (nextProps.exposureType !== this.state.exposureType) {
            this.setState({
                exposureType: nextProps.exposureType
            })
            nextProps.onLoadStart(nextProps.selectedUserItem["key"])
            nextProps.onLoad(agent.Resources.getResourcesTree({'userEmails': [nextProps.selectedUserItem["key"]], 'exposureType': nextProps.exposureType}))
        }
    }

    componentWillMount() {
        if (this.props.selectedUserItem && !this.props.selectedUserItem.resources) {
            this.props.onLoadStart(this.props.selectedUserItem["key"])
            //this.props.onLoad(agent.Resources.getResourcesTree({'userEmails': [this.props.selectedUserItem["key"]], 'exposureType': this.props.exposureType?this.props.exposureType:'EXT'}))
            let getResourcesTree = agent.Resources.getResourcesTree({'userEmails': [this.props.selectedUserItem["key"]], 'exposureType': this.props.exposureType?this.props.exposureType:'EXT'})
            
            if (getResourcesTree['statusCode'] !== 200) {
                console.log("getResourcesTree : ", getResourcesTree)
                this.props.onLoadError("API ERROR")
            }
            else 
                this.props.onLoad(getResourcesTree)    
        }
    }

    onGridReady(params) {
        this.gridApi = params.api;
        this.gridColumnApi = params.columnApi;
        params.api.sizeColumnsToFit();
    }
    render() {
        if (this.props.isResourcesLoading) {
            return (
                <div className="ag-theme-fresh" style={{ height: '200px' }}>
                    <Dimmer active inverted>
                        <Loader inverted content='Loading' />
                    </Dimmer>
                </div>
            )
        }
        else if (this.props.selectedUserItem){
            return (
                <div className="ag-theme-fresh" style={{width: '100%'}}> 
                    <AgGridReact
                        id="myResourceGrid" 
                        domLayout="autoHeight"
                        columnDefs={this.state.columnDefs}
                        rowData={this.props.selectedUserItem.resources}
                        getNodeChildDetails={this.state.getNodeChildDetails}
                        onGridReady={this.onGridReady.bind(this)}
                    />
                </div>
            )
        }
        return null;
    }

}

export default connect(mapStateToProps, mapDispatchToProps)(UserResource);