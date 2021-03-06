import React, { Component } from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom'

import { Statistic, Card, Loader, Dimmer } from 'semantic-ui-react'
import { DASHBOARD_WIDGET_LOADED, DASHBOARD_WIDGET_LOAD_START, SET_REDIRECT_PROPS } from '../../constants/actionTypes';

import agent from '../../utils/agent';

const mapStateToProps = state => ({
    ...state.dashboard
});

const mapDispatchToProps = dispatch => ({
    onLoadStart: (widgetId, payload) =>
        dispatch({ type: DASHBOARD_WIDGET_LOAD_START, widgetId }),
    onLoad: (widgetId, payload) =>
        dispatch({ type: DASHBOARD_WIDGET_LOADED, widgetId, payload }),
    onWidgetClick: (url, states) =>
        dispatch({ type: SET_REDIRECT_PROPS, redirectUrl: url, reducerStates: states })
});

class SimpleNumberWidget extends Component {
    componentWillMount() {
        this.props.onLoadStart(this.props.config.id);
        let payload = {'widget_id': this.props.config.id}
        this.props.onLoad(this.props.config.id, agent.Dashboard.getWidgetData(payload));

    }

    widgetClick = () => {
        this.props.onWidgetClick(this.props.config.link, this.props.config.states)
        this.props.history.push(this.props.config.link)
    }

    render() {

        if (this.props[this.props.config.id]) {
            if (this.props[this.props.config.id].isLoadingWidget) {
                let data = this.props[this.props.config.id].data

                return (
                    <Card onClick={data > 0 ? this.widgetClick : null} >
                        <Card.Content>
                            <Statistic horizontal size="mini" label={this.props.config.header} value={data} />
                        </Card.Content>
                        <Card.Content extra>
                        </Card.Content>
                    </Card>
                )
            }
            else {
                return (
                    <Card>
                        <Card.Content>
                            <Dimmer active inverted>
                                <Loader inverted />
                            </Dimmer>
                        </Card.Content>
                        <Card.Content extra>
                        </Card.Content>
                    </Card>
                )
            }
        }
        return null;
    }
}
export default withRouter(connect(mapStateToProps, mapDispatchToProps)(SimpleNumberWidget));
