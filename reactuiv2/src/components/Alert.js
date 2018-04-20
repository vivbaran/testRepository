import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Loader, Dimmer, Button, Table, Dropdown, Form, Input, Label } from 'semantic-ui-react';
import agent from '../utils/agent';
import {
    ALERTS_LOAD_START,
    ALERTS_LOADED
} from '../constants/actionTypes'

const mapStateToProps = state => ({
    ...state.alert
})

const mapDispatchToProps = dispatch => ({
    alertsLoadingStart: () => 
        dispatch({ type: ALERTS_LOAD_START }),
    alertsLoaded: (payload) => 
        dispatch({ type: ALERTS_LOADED, payload })
})

class Alert extends Component {

    constructor(props) {
        super(props);

        this.state = {
            columnHeaders: [
                "Alert Name",
                "Created At",
                "Severity",
                "Number of Violations",
                "Last Updated"
            ]
        }
    }

    componentWillMount() {
        this.props.alertsLoadingStart()
        this.props.alertsLoaded(agent.Alert.getAlert())
    }

    render () {  
        let tableHeaders = this.state.columnHeaders.map(headerName => {
            return (
                <Table.HeaderCell>{headerName}</Table.HeaderCell>
            )
        })

        let tableRowData = null

        if (this.props.alerts)
            tableRowData = this.props.alerts.map(rowData => {
                return (
                    <Table.Row>
                        <Table.Cell>{rowData["name"]}</Table.Cell>
                        <Table.Cell>{rowData["created_at"]}</Table.Cell>
                        <Table.Cell>{rowData["severity"]}</Table.Cell>
                        <Table.Cell>{rowData["number_of_violations"]}</Table.Cell>
                        <Table.Cell>{rowData["last_updated"]}</Table.Cell>
                    </Table.Row>
                )
            })

        if (this.props.isLoading)
            return (
                <div style={{ height: '200px' }}>
                    <Dimmer active inverted>
                        <Loader inverted content='Loading' />
                    </Dimmer>
                </div>
            )

        return (
            <div>
                <div>
                    <Table celled selectable striped compact='very'>
                        <Table.Header>
                            <Table.Row>
                                {tableHeaders}
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {tableRowData}
                        </Table.Body>
                    </Table>
                </div>
            </div>
        )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(Alert);