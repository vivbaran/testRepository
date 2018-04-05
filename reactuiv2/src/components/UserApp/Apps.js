import React, { Component } from 'react';

import { connect } from 'react-redux';
import { Container, Dimmer, Loader, Grid, Radio } from 'semantic-ui-react';

import agent from '../../utils/agent';

import AppList from './AppList';
import AppDetailsSection from './AppDetailsSection'

import {
  APPS_PAGE_LOADED,
  APPS_PAGE_UNLOADED,
  APPS_PAGE_LOAD_START,
  FLAG_ERROR_MESSAGE
} from '../../constants/actionTypes';


const mapStateToProps = state => ({
  appName: state.common.appName,
  currentApp: state.common.currentApp,
  appsSearchPayload: state.apps.appsSearchPayload,
  appsPayload: state.apps.appPayLoad,
  redirectTo: state.dashboard.redirectTo,
  redirectFilter: state.dashboard.filterType,
  appDeleted: state.apps.appDeleted,
  isLoading: state.apps.isLoading,
  selectedAppItem: state.apps.selectedAppItem
});

const mapDispatchToProps = dispatch => ({
  onLoad: (payload) =>
    dispatch({ type: APPS_PAGE_LOADED, payload }),
  onUnload: () =>
    dispatch({ type: APPS_PAGE_UNLOADED }),
  onLoadStart: () =>
    dispatch({ type: APPS_PAGE_LOAD_START }),
  flagAppsError: (error, info) => 
    dispatch({ type: FLAG_ERROR_MESSAGE, error, info })
});

class Apps extends Component {
  constructor(props) {
    super(props);
    this.state = {
        appsEmpty: false
    }
  }

  componentWillMount(){    
    this.props.onLoadStart();
    this.props.onLoad(agent.Apps.getapps());
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.appsPayload && nextProps.appsPayload.length === 0 && !this.state.appsEmpty) {
      this.props.flagAppsError("There are no apps for user to display", undefined)
      this.setState({
        appsEmpty: true
      })
    }
    if (nextProps.appDeleted !== this.props.appDeleted) {
      nextProps.onLoadStart()
      nextProps.onLoad(agent.Apps.getapps())
    }
  }
  
  render() {
    //const { contextRef } = this.state
    let containerStyle = {
      height: "100%",
      textAlign: "left"
    };

    var gridWidth = 16;
    
    if (this.props.apps.selectedAppItem) {
      gridWidth = 4;
    }

    if (this.props.isLoading && !this.props.selectedAppItem) {
      return (
        <Container style={containerStyle}>
          <Dimmer active inverted>
            <Loader inverted content='Loading' />
          </Dimmer>
        </Container >
      )
    }
    else {
      var appList = (<AppList />)
      var appDetails = this.props.apps.selectedAppItem ? (<Grid.Column width={16 - gridWidth}>
                                                              <AppDetailsSection />
                                                          </Grid.Column>) : ""
      return (
        <Container style={containerStyle}>
          <Grid divided='vertically' stretched>
            {/* <Grid.Row >
              <Grid.Column stretched width="5">
                <Radio name='radioGroup'
                  label='Show all apps'
                  value={0}
                  checked={this.state.scopeExposure === 0}
                  onChange={this.onCheckBoxChecked}
                />
              </Grid.Column>
              <Grid.Column stretched width="5">
                <Radio name='radioGroup'
                  label='Show readonly scope apps'
                  value={1}
                  checked={this.state.scopeExposure === 1}
                  onChange={this.onCheckBoxChecked}
                />
              </Grid.Column>
              <Grid.Column stretched width="5">
                <Radio name='radioGroup'
                  label='Show full scope apps'
                  value={2}
                  checked={this.state.scopeExposure === 2}
                  onChange={this.onCheckBoxChecked}
                />
              </Grid.Column>
            </Grid.Row> */}
            <Grid.Row stretched>
              <Grid.Column stretched width={gridWidth}> 
                {appList}
              </Grid.Column>
            {appDetails}
            </Grid.Row>
          </Grid>
        </Container >

      )
    }

  }
}
export default connect(mapStateToProps, mapDispatchToProps)(Apps);