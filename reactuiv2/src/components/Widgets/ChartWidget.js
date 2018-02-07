import React, { Component } from 'react';
import { connect } from 'react-redux';
import { PieChart } from 'react-chartkick';
import { Statistic, Card, Loader, Segment, Dimmer, Label } from 'semantic-ui-react'
import { DASHBOARD_WIDGET_LOADED, DASHBOARD_WIDGET_LOAD_START } from '../../constants/actionTypes';
import agent from '../../utils/agent';

const mapStateToProps = state => ({
    ...state.dashboard
});

const mapDispatchToProps = dispatch => ({
    onLoadStart: (widgetId, payload) =>
        dispatch({ type: DASHBOARD_WIDGET_LOAD_START, widgetId }),
    onLoad: (widgetId, payload) =>
        dispatch({ type: DASHBOARD_WIDGET_LOADED, widgetId, payload })
});

class ChartWidget extends Component {
    componentWillMount() {
        this.props.onLoadStart(this.props.config.id);
        this.props.onLoad(this.props.config.id, agent.Dashboard.getWidgetData(this.props.config.id));
    }
    render() {
        if (this.props[this.props.config.id]) {
            if (this.props[this.props.config.id].isLoaded) {
                return (
                    <Card>
                        <Card.Content>
                            <PieChart legend="bottom" donut={true} data={this.props[this.props.config.id].data} />

                        </Card.Content>
                        <Card.Content extra>
                            <div className='ui'>
                                <Label color='green'>{this.props.config.footer} </Label>
                            </div>
                        </Card.Content>
                    </Card>
                )
            }
            else {
                return (
                    <Segment>
                        <Dimmer active inverted>
                            <Loader inverted content='Loading' />
                        </Dimmer>
                        <Card>

                            <Card.Content>
                            </Card.Content>
                            <Card.Content extra>
                            </Card.Content>
                        </Card>
                    </Segment>
                )
            }
        }
        return null;
    }
}
export default connect(mapStateToProps, mapDispatchToProps)(ChartWidget);