import React, { Component } from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom'
import { PieChart, BarChart, LineChart } from 'react-chartkick';
import { Card, Loader, Dimmer, Label } from 'semantic-ui-react'
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

class ChartWidget extends Component {
    componentWillMount() {
        this.props.onLoadStart(this.props.config.id);
        let filters = {'event_filters': this.props.filters !== undefined?this.props.filters:{}};
        let payload = {'widget_id': this.props.config.id}
        Object.assign(payload, filters)
        this.props.onLoad(this.props.config.id, agent.Dashboard.getWidgetData(payload));
    }

    componentWillReceiveProps(nextProps){
       if(nextProps.filters !== this.props.filters){
         let filters ={'event_filters': nextProps.filters !== undefined?nextProps.filters:{}};
         let payload = {'widget_id': nextProps.config.id}
         Object.assign(payload, filters)
         agent.Dashboard.getWidgetData(payload)
       }
    }

    widgetClick = () => {
        this.props.onWidgetClick(this.props.config.link, this.props.config.states)
        this.props.history.push(this.props.config.link)
    }

    render() {
        if (this.props[this.props.config.id]) {
            if (this.props[this.props.config.id].isLoadingWidget) {
                // if (!this.props[this.props.config.id].data.totalCount)
                //     return null
                let chart = null
                let maxLimit = null
                if(this.props.config.id == 'expensesByCategory'){
                    if(! Number(this.props[this.props.config.id].data.totalCount))
                        maxLimit = 10
                    chart = <BarChart min={0} max={maxLimit} prefix="$" thousands="," label="Annual Cost/Category" legend="bottom"  data={this.props[this.props.config.id].data.rows} />
                }
                else if(this.props.config.id == 'activitiesByEventType'){
                    chart = <LineChart min={0} max={maxLimit} thousands="," label="Events" legend="bottom"  data={this.props[this.props.config.id].data} />
                }
                else if (this.props.config.id === 'filesWithFileType') {
                    chart = <PieChart legend="bottom" donut={true} data={this.props[this.props.config.id].data.rows} />
                }
                else {
                    var color = ['#db4437', '#e68a00', '#fbbd08', '#4285f4']
                    if (this.props.config.id === 'userAppAccess')
                        color = ['#db4437', '#fbbd08', '#4285f4']
                    chart = <PieChart legend="bottom" donut={true} data={this.props[this.props.config.id].data.rows} colors={color} />
                }

                return (
                        <Card >
                            <Card.Content>
                                {chart}
                            </Card.Content>
                            <Card.Content extra onClick={this.widgetClick} >
                                <div className='ui'>
                                    <Label color='green'>{this.props[this.props.config.id].data.totalCount}
                                        &nbsp;{this.props.config.footer}</Label>
                                </div>
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
export default withRouter(connect(mapStateToProps, mapDispatchToProps)(ChartWidget));
