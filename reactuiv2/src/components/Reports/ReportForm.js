import React, { Component, PropTypes } from 'react';
import { Route, Switch, Redirect } from 'react-router-dom';
import {Card, Button, Form, Header, Modal, Checkbox, Input} from 'semantic-ui-react'
import ReactCron from '../reactCron/index'
import { connect } from 'react-redux';
import UsersTree from '../Users/UsersTree';
import ResourcesList from '../Resources/ResourcesList';
import agent from '../../utils/agent';
import * as Helper from '../reactCron/helpers/index';
import serializeForm from 'form-serialize';


import {
  CREATE_SCHEDULED_REPORT,
  UPDATE_SCHEDULED_REPORT
} from '../../constants/actionTypes';

const mapStateToProps = state => ({
    ...state.reports,
    ...state.users,
    ...state.resources
  });

const mapDispatchToProps = dispatch => ({
    addScheduledReport: (report) => {
      dispatch({ type: CREATE_SCHEDULED_REPORT, payload: agent.Scheduled_Report.createReport(report) })
    },
    updateScheduledReport: (report) => {
      dispatch({ type: UPDATE_SCHEDULED_REPORT, payload: agent.Scheduled_Report.updateReport(report)})
    }

  });

const reportOptions = [
{  text: 'Access Permission Report', value: 'Permission' },
{  text: 'Activity Log Report', value: 'Activity' },
]

class ReportForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      value:{},
      cronExpression: '',
      reportType: '',
      reportNameError: false,
      emailToError: false,
      valueError: false,
      cronExpressionError: false,
      IsActiveError: false,
      reportTypeError: false,
      error: '',
      reportDataForReportId: this.props.reportsMap,
      finalReportObj: {}

    }
  }


  submit = () => {

    var errorMessage = ""
    var success = false
    var pattern = /^\s*$/;
    let valid = true
    var emailCheck  = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    var selected_entity;

    var copyFinalInputObj = {}
    Object.assign(copyFinalInputObj, this.state.finalReportObj)
    if(this.state.finalReportObj['selected_entity_type']){

      if(this.state.finalReportObj['selected_entity_type'] === "group" ){
        if(this.props.rowData){
          selected_entity = this.props.rowData.key
        }
      }
      else if (this.state.finalReportObj['selected_entity_type'] === "resource") {
        if(this.props.rowData){
          selected_entity = this.props.rowData.resourceId
        }
      }
     copyFinalInputObj["selected_entity"] = selected_entity
    }


    if(!copyFinalInputObj['is_active']){
      copyFinalInputObj['is_active'] = 0
    }

    var populatedDataForParticularReport ={}
    if(this.props.formType === 'modify_report'){
      var populatedDataForParticularReport = this.state.reportDataForReportId
      Object.assign(populatedDataForParticularReport, copyFinalInputObj)
    }


    if(!copyFinalInputObj.name && !populatedDataForParticularReport.name){
      errorMessage = "Please enter a name for this report."
      valid = false
    }
    else if(!copyFinalInputObj.report_type && !populatedDataForParticularReport.report_type){
      errorMessage = " Please select the report type."
      valid = false
    }
    else if(!copyFinalInputObj.selected_entity_type && !populatedDataForParticularReport.selected_entity_type){
      errorMessage = "Please select User/Group or File/Folder."
      valid = false
    }
    else if(!copyFinalInputObj.selected_entity && !populatedDataForParticularReport.selected_entity){
      errorMessage = "Please select the entity "
      valid = false
    }
    else if(!copyFinalInputObj.receivers && !populatedDataForParticularReport.receivers){
      errorMessage = "Please enter an email address."
      valid = false
    }


    if(valid && this.props.formType === 'modify_report'){
      copyFinalInputObj['report_id'] = this.state.reportDataForReportId['report_id']

      success = true
      this.props.updateScheduledReport(copyFinalInputObj)
      this.props.close()
    }
    else if (valid && this.props.formType === 'create_report') {
      success = true
      this.props.addScheduledReport(copyFinalInputObj)
      this.props.close()

    }

    if(!success){
      this.setState((state) => ({
        error: errorMessage
      }))

    }

  }

  stateSetHandler = (data) => {
      this.setState({
        cronExpression: data
      })
  }

  handleMultipleOptions = (data) => {

    var value = Object.keys(this.state.reportDataForReportId).length>0 ?
                 this.state.reportDataForReportId[data] : null

    return value
  }

  onChangeReportInput = (key, value) => {
    var copyFinalReportObj = {};
    Object.assign(copyFinalReportObj, this.state.finalReportObj)

    if(key === 'frequency'){
      value = "cron(" + value + ")"
    }

    copyFinalReportObj[key] = value

    if(key === 'selected_entity_type'){
      if(Object.keys(this.state.reportDataForReportId).length>0){
          var reportsMapcopy ={}
          Object.assign(reportsMapcopy, this.state.reportDataForReportId)
          reportsMapcopy['selected_entity_type'] = "";
          this.setState({
            reportDataForReportId: reportsMapcopy
          })
      }
      else {

      }


    }

    this.setState({
      finalReportObj: copyFinalReportObj,
      value: value
    })

  }



  render() {

    let user = this.props.rowData
    const { value } = this.state

    var modalContent = (
      <div>

        <div style = {{color:'red'}}>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{this.state.error}</div>
          <Form onSubmit={this.submit}>
          <div className="ui two column very relaxed grid">
            <div className="column">

              <div className="ui form">
                  <Form.Field>
                    <Checkbox onChange={(e, data) => this.onChangeReportInput('is_active', data.checked)} label='IsActive' width={2}
                      />
                  </Form.Field>
                  <Form.Input onChange={(e) => this.onChangeReportInput('name', e.target.value)}
                  label='Name' placeholder='Name'  defaultValue={this.props.reportsMap['name']} />

                  <Form.Input onChange={(e) => this.onChangeReportInput('description', e.target.value)} label='Description' placeholder='Description'
                    defaultValue={this.props.reportsMap['description']}/>

                  <Form.Select  id='reportType' onChange={(e, data) => this.onChangeReportInput('report_type', data.value)}
                    label='Report Type' options={reportOptions} placeholder='Report Type'
                    defaultValue={this.handleMultipleOptions('report_type')} />

                <Form.Input onChange={(e) => this.onChangeReportInput('receivers', e.target.value)}
                  label='Email To' placeholder='Email To' control={Input}
                  defaultValue={this.props.reportsMap['receivers']}/>
                  <Form.Field >
                    <ReactCron ref='reactCron' stateSetHandler ={this.onChangeReportInput} />
                  </Form.Field>

              </div>

            </div>
            <div className="column">
                <Form.Group inline>
                  <Form.Radio label='File/Folder' value='resource'
                    checked={this.handleMultipleOptions('selected_entity_type') === 'resource' || value === 'resource'}
                    onChange={(e, data) => this.onChangeReportInput('selected_entity_type', data.value)}
                     />
                  <Form.Radio label='Group/User' value='group'
                    checked={this.handleMultipleOptions('selected_entity_type') === 'group' || value === 'group'}
                    onChange={(e, data) => this.onChangeReportInput('selected_entity_type', data.value)}
                    />
                </Form.Group>
                {this.state.value == 'group'?
                   <Form.Field><UsersTree />
                    </Form.Field> : null}
                   {this.state.value == 'resource'? <Form.Field ><ResourcesList /></Form.Field> : null}
            </div>
          </div>
          </Form>
      </div>
    )


    return(
      <div>
        <Modal className="scrolling"
         open={this.props.showModal}>
          <Modal.Content>
            {modalContent}
          </Modal.Content>
          <Modal.Actions>
            <Button onClick={this.props.close}>Close</Button>
            <Button content="Submit" onClick={this.submit} />
          </Modal.Actions>
        </Modal>
     </div>
   )
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(ReportForm);
