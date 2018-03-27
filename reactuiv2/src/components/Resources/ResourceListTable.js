import React, { Component } from 'react';
import { connect } from 'react-redux';

import { Loader, Dimmer, Button, Table, Dropdown, Input } from 'semantic-ui-react';

import agent from '../../utils/agent';
import { IntlProvider, FormattedRelative } from 'react-intl';
import DatePicker from 'react-datepicker'
import moment from 'moment'
import Moment from 'react-moment'
import 'react-datepicker/dist/react-datepicker.css'
import ResourceSearch from '../Search/ResourceSearch'

import {
    RESOURCES_PAGE_LOADED,
    RESOURCES_PAGE_LOAD_START,
    RESOURCES_TREE_SET_ROW_DATA,
    RESOURCES_PAGINATION_DATA,
    RESOURCES_FILTER_CHANGE
} from '../../constants/actionTypes';


const mapStateToProps = state => ({
    ...state.resources
});

const mapDispatchToProps = dispatch => ({
    onLoadStart: () => dispatch({ type: RESOURCES_PAGE_LOAD_START }),
    onLoad: (payload) => dispatch({ type: RESOURCES_PAGE_LOADED, payload }),
    setRowData: (payload) => dispatch({ type: RESOURCES_TREE_SET_ROW_DATA, payload }),
    setPaginationData: (pageNumber, pageLimit) => dispatch({ type: RESOURCES_PAGINATION_DATA, pageNumber, pageLimit }),
    resetPaginationData: (pageNumber, pageLimit) => dispatch({ type: RESOURCES_PAGINATION_DATA, pageNumber, pageLimit }),
    changeFilter: (property, value) => dispatch({ type: RESOURCES_FILTER_CHANGE, property, value })
});

class ResourcesListTable extends Component {
    constructor(props) {
        super(props);

        this.state = {
            columnHeaders: [
                "Name",
                "Type",
                "Owner",
                "Exposure Type",
                "Parent Folder",
                "Modified On or Before"
            ],
            filterResourceType: "",
            filterEmailId: "",
            filterParentFolder: "",
            currentDate: ""
        }

        this.exposureFilterOptions = [
            {
                text: 'Externally Shared',
                value: 'EXT'
            },
            {
                text: 'Domain Shared',
                value: 'DOMAIN'
            },
            {
                text: 'Internally Shared',
                value: 'INT'
            },
            {
                text: 'All Files',
                value: 'ALL'
            },
            {
                text: 'Publicly Shared',
                value: 'PUBLIC'
            }
        ]
    }

    componentWillMount() {
        // if (!this.props.pageNumber)
        //     this.props.setPaginationData(0, 100)

        this.props.onLoadStart()
        this.props.onLoad(agent.Resources.getResourcesTree({ 'userEmails': [], 'exposureType': this.props.filterExposureType, 'resourceType': this.props.filterResourceType, 'pageNumber': this.props.pageNumber, 'pageSize': this.props.pageLimit }))
    }

    componentWillUnmount() {
        this.props.resetPaginationData(0, 100)
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps !== this.props) {
            if (nextProps.filterExposureType !== this.props.filterExposureType || nextProps.filterResourceType !== this.props.filterResourceType ||
                nextProps.pageNumber !== this.props.pageNumber || nextProps.filterEmailId !== this.props.filterEmailId || nextProps.filterParentFolder !== this.props.filterParentFolder || nextProps.filterByDate !== this.props.filterByDate) {
                nextProps.onLoadStart()
                nextProps.onLoad(agent.Resources.getResourcesTree({ 'userEmails': [], 'exposureType': nextProps.filterExposureType, 'resourceType': nextProps.filterResourceType, 'pageNumber': nextProps.pageNumber, 'pageSize': nextProps.pageLimit, 'ownerEmailId': nextProps.filterEmailId, 'parentFolder': nextProps.filterParentFolder, 'selectedDate': nextProps.filterByDate }))
            }
            if (nextProps.filterResourceType !== this.state.filterResourceType)
                this.setState({
                    filterResourceType: nextProps.filterResourceType
                })
        }
    }

    handleClick = (event, rowData) => {
        event.preventDefault()
        this.props.setRowData(rowData)
    }

    handleExposureTypeChange = (event, data) => {
        let value = data.value === 'ALL' ? '' : data.value
        if (value !== this.props.filterExposureType)
            this.props.changeFilter("filterExposureType", value);
    }

    handleResourceTypeChange = (event) => {
        this.setState({
            filterResourceType: event.target.value
        });
    }

    handleEmailIdChange = (event) => {
        this.setState({
            filterEmailId: event.target.value
        })
    }

    handleParentFolderChange = (event) => {
        this.setState({
            filterParentFolder: event.target.value
        })
    }

    handleDateChange = (date) => {
        let selectedDate = date.format('YYYY-MM-DD HH:MM:SS')
        this.setState({
            currentDate: date
        })
        this.props.changeFilter("filterByDate", selectedDate)
    }

    handleKeyPress = (event, filterType, filterValue) => {
        if (event.key === 'Enter') {
            this.props.changeFilter(filterType, filterValue);
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
            return (
                <Table.HeaderCell>{headerName}</Table.HeaderCell>
            )
        })

        let tableRowData = null
        let resourceData = null

        if (this.props.resourceSearchPayload)
            resourceData = this.props.resourceSearchPayload
        else if (this.props.resourceTree)
            resourceData = this.props.resourceTree

        if (resourceData)
            tableRowData = resourceData.map(rowData => {
                //console.log("lastmodifiedtime : ", rowData["last_modified_time"])
                return (
                    <Table.Row onClick={(event) => this.handleClick(event, rowData)} style={this.props.rowData === rowData ? { 'background-color': '#2185d0' } : null}>
                        <Table.Cell>{rowData["resource_name"]}</Table.Cell>
                        <Table.Cell width='2'>{rowData["resource_type"]}</Table.Cell>
                        <Table.Cell>{rowData["resource_owner_id"]}</Table.Cell>
                        <Table.Cell textAlign='center'>{rowData["exposure_type"]}</Table.Cell>
                        <Table.Cell width='3'>{rowData["parent_name"]}</Table.Cell>
                        <Table.Cell width='2'><IntlProvider locale='en'><FormattedRelative value={rowData["last_modified_time"]} /></IntlProvider ></Table.Cell>
                    </Table.Row>
                )
            })

        let dimmer = (
            <Dimmer active inverted>
                <Loader inverted content='Loading' />
            </Dimmer>
        )

        if (this.props.isLoading || resourceData) {
            let filterMetadata = { 'userEmails': [], 'exposureType': this.props.filterExposureType, 'resourceType': this.props.filterResourceType, 'pageNumber': this.props.pageNumber, 'pageSize': this.props.pageLimit, 'ownerEmailId': this.props.filterEmailId, 'parentFolder': this.props.filterParentFolder, 'selectedDate': this.props.filterByDate }
            return (
                <div>
                    <div style={{ 'minHeight': this.props.rowData?null:document.body.clientHeight/2, 'maxHeight': document.body.clientHeight/1.05, 'overflow': 'auto', 'cursor': 'pointer' }}>
                        <Table celled selectable striped compact='very' sortable>
                            <Table.Header>
                                <Table.Row>
                                    {tableHeaders}
                                </Table.Row>
                            </Table.Header>
                            <Table.Body>
                                <Table.Row>
                                    <Table.Cell>
                                        <ResourceSearch filterMetadata={filterMetadata} />
                                    </Table.Cell>
                                    <Table.Cell>
                                        <Input fluid placeholder='Filter by type...' value={this.state.filterResourceType} onChange={this.handleResourceTypeChange} onKeyPress={(event) => this.handleKeyPress(event,"filterResourceType",this.state.filterResourceType)} />
                                    </Table.Cell>
                                    <Table.Cell>
                                        <Input fluid placeholder='Filter by email...' value={this.state.filterEmailId} onChange={this.handleEmailIdChange} onKeyPress={(event) => this.handleKeyPress(event,"filterEmailId",this.state.filterEmailId)} />
                                    </Table.Cell>
                                    <Table.Cell>
                                        <Dropdown
                                            fluid
                                            options={this.exposureFilterOptions}
                                            selection
                                            value={this.props.filterExposureType === '' ? 'ALL' : this.props.filterExposureType}
                                            onChange={this.handleExposureTypeChange}
                                        />
                                    </Table.Cell>
                                    <Table.Cell>
                                        <Input fluid placeholder='Filter by folder...' value={this.state.filterParentFolder} onChange={this.handleParentFolderChange} onKeyPress={(event) => this.handleKeyPress(event,"filterParentFolder",this.state.filterParentFolder)} />
                                    </Table.Cell>
                                    <Table.Cell>
                                        {/* <Input as={datePicker} fluid placeholder='Filter by date...' /> */}
                                        <DatePicker 
                                            selected={this.state.currentDate} 
                                            onChange={this.handleDateChange} 
                                            showTimeSelect 
                                            dateFormat="LLL"
                                        />
                                    </Table.Cell>
                                </Table.Row>
                                {tableRowData}
                            </Table.Body>
                            {this.props.isLoading ? dimmer : null}
                        </Table>
                    </div>
                    <div style={{ marginTop: '5px' }} >
                        {(!tableRowData || tableRowData.length < this.props.pageLimit) ? null : (<Button color='green' size="mini" style={{ float: 'right', width: '80px' }} onClick={this.handleNextClick} >Next</Button>)}
                        {this.props.pageNumber > 0 ? (<Button color='green' size="mini" style={{ float: 'right', width: '80px' }} onClick={this.handlePreviousClick} >Previous</Button>) : null}
                    </div>
                </div>
            )
        }
        else
            return (
                <div style={{ textAlign: 'center' }}>
                    No Resources to display for user 
                </div>
            )
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(ResourcesListTable);