import React, { Component } from 'react';
import { connect } from 'react-redux';

import { Statistic, Card, Loader, Segment, Dimmer } from 'semantic-ui-react'
import { USERS_TREE_LOADED, 
         USERS_TREE_LOAD_START,
         USERS_TREE_SET_ROW_DATA,
         SELECTED_USER_PARENTS_NAME 
        } from '../../constants/actionTypes';
import agent from '../../utils/agent';

import { AgGridReact } from "ag-grid-react";
import 'ag-grid/dist/styles/ag-grid.css';
import 'ag-grid/dist/styles/ag-theme-fresh.css';

const mapStateToProps = state => ({
    ...state.users
});

const mapDispatchToProps = dispatch => ({
    onLoadStart: () =>
        dispatch({ type: USERS_TREE_LOAD_START }),
    onLoad: (payload) =>
        dispatch({ type: USERS_TREE_LOADED, payload }),
    setRowData: (payload) => 
        dispatch({type: USERS_TREE_SET_ROW_DATA, payload}),
    setSelectedUserParents: (payload) =>
        dispatch({type: SELECTED_USER_PARENTS_NAME,payload})
});

class UsersTree extends Component {
    constructor(props) {
        super(props);
        this.onCellClicked = this.onCellClicked.bind(this);
        
        this.state = {
            cellData: '',
            columnDefs: [
                {
                    headerName: "Type",
                    field: "type",
                    hide: true,
                    sort: "asc",
                    cellRenderer: "agGroupCellRenderer",
                    cellStyle: {textAlign: "left"}
                },
                {
                    headerName: "Users and Groups",
                    field: "name",
                    sort: "asc",
                    cellRenderer: "agGroupCellRenderer",
                    cellStyle: {textAlign: "left"}
                }
            ],
            getNodeChildDetails: rowItem => {
                //console.log("node child details : ", rowItem)
                if (!rowItem.member_type) {
                    var rows = [];
                    if (rowItem.children) {
                        for (var index = 0; index < rowItem.children.length; index++) {
                            var childKey = rowItem.children[index];
                            var row = this.props.usersTree[childKey];
                            row.key = childKey;
                            rows.push(row);
                        }
                        return {
                            group: true,
                            expanded: false,
                            children: rows,
                            key: rowItem.key
                        };
                    }
                    return {
                        group: true,
                        expanded: false,
                        children: []
                    }
                } else {
                    return null;
                }
            }
        };
        
        this.gridOptions = {
            onRowClicked: this.onCellClicked
        }
    }

    onCellClicked(params) {
        console.log("cell click data : ", params.data)
        this.setState({
            cellData: params.data
        })
        this.props.setRowData(params.data);
        
        let selectedUserEmail = params.data["key"]
        //console.log("rowdatakey : ", selectedUserEmail)
        let selectedUserParentsEmail = params.data["parents"]
        let selectedUserParentsName = selectedUserParentsEmail.map((parent,index) => {
            return this.props.usersTree[parent]["name"]
        })
        console.log("selectedUserParentsName : ", selectedUserParentsName)
        this.props.setSelectedUserParents(selectedUserParentsName)
    }

    componentWillMount() {
        this.props.onLoadStart();
        this.props.onLoad(agent.Users.getUsersTree());
        //console.log("resources tree : ", agent.Resources.getResourcesTree())
    }
    onGridReady(params) {
        this.gridApi = params.api;
        this.gridColumnApi = params.columnApi;

        params.api.sizeColumnsToFit();
    }
    getTreeRows() {
        console.log("usersTree is : ", this.props.usersTree)
        var rows = [];
        var keys = Object.keys(this.props.usersTree);

        for (var index = 0; index < keys.length; index++) {
            var row = this.props.usersTree[keys[index]];
            row.key = keys[index];
            row.type = "group";
            if (!row.name)
            {
                row.type = "user";
                row.name = row.firstName + " " + row.lastName + " [" + keys[index] + "]";
            } 
            rows.push(row);
        }
        console.log("users tree rows : ", rows)
        return rows;
    }
    render() {
        if (!this.props.usersTree) {
            if (this.props.isLoading) {
                return (
                    <div className="ag-theme-fresh" style={{ height: '200px' }}>
                        <Dimmer active inverted>
                            <Loader inverted content='Loading' />
                        </Dimmer>
                    </div>
                )
            }
            else {
                return null;
            }
        }
        else {
            return (
                <div className="ag-theme-fresh">
                    <AgGridReact
                        id="myGrid" domLayout="autoHeight"
                        columnDefs={this.state.columnDefs}
                        rowData={this.getTreeRows()}
                        getNodeChildDetails={this.state.getNodeChildDetails.bind(this)}
                        onGridReady={this.onGridReady.bind(this)}
                        gridOptions={this.gridOptions}
                    />
                </div>
            )
        }

    }
}
export default connect(mapStateToProps, mapDispatchToProps)(UsersTree);