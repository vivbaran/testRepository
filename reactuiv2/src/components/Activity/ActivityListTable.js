import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Loader, Dimmer, Button, Table, Input, Icon, Label, Modal, Header, Form } from 'semantic-ui-react';
import agent from '../../utils/agent';
import { IntlProvider, FormattedRelative } from 'react-intl';
import DatePicker from 'react-datepicker'
import { LineChart } from 'react-chartkick';
import Mustache from 'mustache'


import {
    ACTIVITIES_PAGE_LOAD_START,
    ACTIVITIES_PAGE_LOADED,
    ACTIVITIES_CHART_LOAD_START,
    ACTIVITIES_CHART_LOADED,
    ACTIVITIES_SET_ROW_DATA,
    ACTIVITIES_PAGINATION_DATA,
    ACTIVITIES_FILTER_CHANGE
} from '../../constants/actionTypes';


const mapStateToProps = state => ({
    ...state.common,
    ...state.activity
});

const mapDispatchToProps = dispatch => ({
    onLoadStart: () => dispatch({ type: ACTIVITIES_PAGE_LOAD_START }),
    onLoad: (payload) => dispatch({ type: ACTIVITIES_PAGE_LOADED, payload }),
    onChartLoadStart: () => dispatch({ type: ACTIVITIES_CHART_LOAD_START }),
    onChartLoad: (payload) => dispatch({ type: ACTIVITIES_CHART_LOADED, payload }),
    setRowData: (payload) => dispatch({ type: ACTIVITIES_SET_ROW_DATA, payload }),
    setPaginationData: (pageNumber, pageLimit) => dispatch({ type: ACTIVITIES_PAGINATION_DATA, pageNumber, pageLimit }),
});

class ActivityListTable extends Component {
    constructor(props) {
        super(props);

        this.state = {
            columnHeaders: [
                "Source",
                "Event Type",
                "Time Since",
                "User",
                "Details"
            ],
            currentDate: '',
            domain_id: this.props.currentUser['domain_id'],
            filterConnectorType: "",
            filterEventType: "",
            filteractor: "",
            columnHeaderDataNameMap: {
                "Timestamp": "timestamp",
                "Connector": "connector_type",
                "Actor": "actor",
                "Event Type": "event_type"
            }
        }
    }

    componentWillMount() {
        this.props.onLoadStart();
        this.props.onChartLoadStart();
        this.props.onChartLoad(agent.Dashboard.getWidgetData({ 'widget_id': 'activitiesByEventType', 'event_filters': {} }))
    }

    componentWillUnmount() {
        this.props.setPaginationData(0, 100)
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps !== this.props) {
            if (nextProps.filterConnectorType !== this.props.filterConnectorType || nextProps.filterEventType !== this.props.filterEventType ||
                nextProps.pageNumber !== this.props.pageNumber || nextProps.filteractor !== this.props.filteractor || nextProps.filterByDate !== this.props.filterByDate) {
                nextProps.onLoadStart()

                let selectedConnectors = []
                let selectedEventTypes = []
                let timeStamp = 'filterByDate' in nextProps ? nextProps['filterByDate'] : ''
                let filteractor = 'filteractor' in nextProps ? nextProps['filteractor'] : ''
                if('filterEventType' in nextProps){
                    for(let k in nextProps.filterEventType){
                        if(nextProps.filterEventType[k]){
                            selectedEventTypes.push(k)
                        }
                    }
                }
                if('filterConnectorType' in nextProps){
                    for(let k in nextProps.filterConnectorType){
                        if(nextProps.filterConnectorType[k]){
                            selectedConnectors.push(k)
                        }
                    }
                }
                
                nextProps.onLoad(agent.Activity.getAllActivites({
                    'domain_id': this.state.domain_id, 'timestamp': timeStamp, 'actor': filteractor,
                    'connector_type': selectedConnectors, 'event_type': selectedEventTypes, 'pageNumber': nextProps.pageNumber, 'pageSize': nextProps.pageLimit
                }))
            }
        }
    }

    handleClick = (event, rowData) => {
        event.preventDefault()
        this.props.setRowData(rowData)
    }


    handleColumnSort = (mappedColumnName) => {
        if (this.state.columnNameClicked !== mappedColumnName) {
            this.props.onLoadStart()

            this.props.onLoad(agent.Activity.getAllActivites({
                'domain_id': this.state.domain_id, 'timestamp': this.props.filterByDate, 'actor': this.props.filteractor,
                'connector_type': this.props.filterConnectorType, 'event_type': this.props.filterEventType,
                'pageNumber': this.props.pageNumber, 'pageSize': this.props.pageLimit, 'sortColumn': mappedColumnName, 'sortType': 'asc'
            }))
            this.setState({
                columnNameClicked: mappedColumnName,
                sortOrder: 'ascending'
            })
        }
        else {
            this.props.onLoadStart()

            this.props.onLoad(agent.Activity.getAllActivites({
                'domain_id': this.state.domain_id, 'timestamp': this.props.filterByDate, 'actor': this.props.filteractor,
                'connector_type': this.props.filterConnectorType, 'event_type': this.props.filterEventType, 'pageNumber': this.props.pageNumber,
                'pageSize': this.props.pageLimit, 'sortColumn': mappedColumnName, 'sortType': this.state.sortOrder === 'ascending' ? 'desc' : 'asc'
            }))
            this.setState({
                sortOrder: this.state.sortOrder === 'ascending' ? 'descending' : 'ascending'
            })
        }
    }

    handleNextClick = () => {
        this.props.setPaginationData(this.props.pageNumber + 1, this.props.pageLimit)
    }

    handlePreviousClick = () => {
        this.props.setPaginationData(this.props.pageNumber - 1, this.props.pageLimit)
    }

    render() {
        let tableHeaders = this.state.columnHeaders.map(headerName => {
            let mappedColumnName = this.state.columnHeaderDataNameMap[headerName]
            return (
                <Table.HeaderCell key={headerName}
                    sorted={this.state.columnNameClicked === mappedColumnName ? this.state.sortOrder : null}
                    onClick={() => this.handleColumnSort(mappedColumnName)} >
                    {headerName}
                </Table.HeaderCell>
            )
        })

        let tableRowData = null
        let activitiesData = null

        if (this.props.activitySearchPayload)
            activitiesData = this.props.activitySearchPayload
        else if (this.props.activitiesDataPayload)
            activitiesData = this.props.activitiesDataPayload

        if (activitiesData)
            tableRowData = activitiesData.map(rowData => {
                let event_type = rowData["event_type"]
                let activity_index = this.props.all_activity_events_map[event_type]
                let activity_template = this.props.all_activity_events[activity_index] ? this.props.all_activity_events[activity_index][1]['event_template'] : ''
                activity_template = Mustache.to_html(activity_template, rowData)
                
                let labelStyle = {
                    'max-width': '200px',
                    'white-space': 'nowrap',
                    'overflow': 'hidden',
                    'text-overflow': 'ellipsis'
                }
                return (
                    <Table.Row key={rowData['_id']} onClick={(event) => this.handleClick(event, rowData)} style={this.props.rowData === rowData ? { 'backgroundColor': '#2185d0' } : null}>
                        <Table.Cell>{rowData["connector_type"]}</Table.Cell>
                        <Table.Cell>{event_type}</Table.Cell>
                        <Table.Cell><IntlProvider locale='en'><FormattedRelative value={rowData["timestamp"]} /></IntlProvider ></Table.Cell>
                        <Table.Cell>{rowData["actor"]}</Table.Cell>
                        {/* <Table.Cell width='3'><Label color='blue' style={labelStyle}>{activity_desc}</Label></Table.Cell> */}
                        <Table.Cell>{activity_template}</Table.Cell>
                    </Table.Row>
                )
            })

        let dimmer = (
            <Dimmer active inverted>
                <Loader inverted content='Loading' />
            </Dimmer>
        )

        if (this.props.isLoadingActivities || activitiesData) {
            let filterMetadata = {
                'timestamp': this.props.filterByDate, 'actor': this.props.filteractor,
                'connector_type': this.props.filterConnectorType, 'event_type': this.props.filterEventType
            }
            return (
                <div>
                    <LineChart thousands="," label="Events" legend="bottom" data={this.props.activitiesChartDataPayload} />
                    <div ref="table" style={{ 'minHeight': document.body.clientHeight / 2.3, 'maxHeight': document.body.clientHeight / 2.3, 'overflow': 'auto', 'cursor': 'pointer' }}>
                        <Table celled selectable striped compact='very' sortable>
                            <Table.Header style={{ 'position': 'sticky', 'top': '50px', 'width': '100%' }}>
                                <Table.Row>
                                    {tableHeaders}
                                </Table.Row>
                            </Table.Header>
                            <Table.Body>
                                {tableRowData}
                            </Table.Body>
                        </Table>
                        {this.props.isLoadingActivities ? dimmer : null}
                    </div>
                    <div style={{ marginTop: '10px' }} >
                        <div style={{ float: 'right' }}>
                            {this.props.pageNumber > 0 ? (<Button color='green' size="mini" style={{ width: '80px' }} onClick={this.handlePreviousClick} >Previous</Button>) : null}
                            {(!tableRowData || tableRowData.length < this.props.pageLimit) ? null : (<Button color='green' size="mini" style={{ width: '80px' }} onClick={this.handleNextClick} >Next</Button>)}
                        </div>
                    </div>
                </div>
            )
        }
        else {
            return (
                <div style={{ textAlign: 'center' }}>
                    No Activities to display for domain
          </div>
            )
        }

    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ActivityListTable);
