import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Loader, Dimmer, Button, Table, Dropdown, Form, Input, Label } from 'semantic-ui-react';
import agent from '../utils/agent';
import Mustache from 'mustache';
import {
    ALERTS_LOAD_START,
    ALERTS_LOADED
} from '../constants/actionTypes'
import DateComponent from './DateComponent';

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
                "Severity",
                "Description",
                "Number of Violations",
                "Last Updated"
            ]
        }
    }

    componentWillMount() {
        this.props.alertsLoadingStart()
        this.props.alertsLoaded(agent.Alert.getAlert())
    }

    render() {
        let tableHeaders = this.state.columnHeaders.map((headerName, index) => {
            return (
                <Table.HeaderCell key={index}>{headerName}</Table.HeaderCell>
            )
        })

        let tableRowData = null

        if (this.props.alerts && this.props.alerts.length)
            tableRowData = this.props.alerts.map((rowData, index) => {
                let desc = rowData["description_template"]
                let payload = JSON.parse(rowData["payload"])
                if (desc && payload) {
                    desc = Mustache.to_html(desc, payload)
                }
                else {
                    desc = rowData["name"]
                }
                return (
                    <Table.Row key={index}>
                        <Table.Cell>{rowData["name"]}</Table.Cell>
                        <Table.Cell>{rowData["severity"]}</Table.Cell>
                        <Table.Cell>{desc} </Table.Cell>
                        <Table.Cell>{rowData["number_of_violations"]}</Table.Cell>
                        <Table.Cell><DateComponent value={rowData["last_updated"]} /></Table.Cell>
                    </Table.Row>
                )
            })

        if (this.props.isLoadingAlert)
            return (
                <div style={{ height: '200px' }}>
                    <Dimmer active inverted>
                        <Loader inverted content='Loading' />
                    </Dimmer>
                </div>
            )
        else if (tableRowData)
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
        else
            return (
                <div>
                    No alerts to display
                </div>
            )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(Alert);
