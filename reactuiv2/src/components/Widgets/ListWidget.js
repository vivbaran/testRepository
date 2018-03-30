import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom'
import { Table, Card, Loader, Dimmer, Label } from 'semantic-ui-react'
import { DASHBOARD_WIDGET_LOADED, DASHBOARD_WIDGET_LOAD_START, SET_CURRENT_URL } from '../../constants/actionTypes';
import agent from '../../utils/agent';

const mapStateToProps = state => ({
    ...state.dashboard
});

const mapDispatchToProps = dispatch => ({
    onLoadStart: (widgetId, payload) =>
        dispatch({ type: DASHBOARD_WIDGET_LOAD_START, widgetId }),
    onLoad: (widgetId, payload) =>
        dispatch({ type: DASHBOARD_WIDGET_LOADED, widgetId, payload }),
    onWidgetClick: (url) => 
        dispatch({ type: SET_CURRENT_URL, url })
});

class ListWidget extends Component {
    componentWillMount() {
        this.props.onLoadStart(this.props.config.id);
        this.props.onLoad(this.props.config.id, agent.Dashboard.getWidgetData(this.props.config.id));
    }

    widgetClick = () => {
        this.props.onWidgetClick(this.props.config.link)
    }

    render() {

        if (this.props[this.props.config.id]) {
            if (this.props[this.props.config.id].isLoaded) {
                const data = this.props[this.props.config.id].data.rows;
                const count = this.props[this.props.config.id].data.totalCount;
                const remainingCount = count - data.length
                const footer = count >= 5?"...and " + remainingCount + " more":null;                
                
                if (!count)
                    return null
                
                return (
                    <Card as={Link} to={this.props.config.link} onClick={this.widgetClick} >
                        <Card.Content>
                            <Table celled singleline='false'>
                                <Table.Header>
                                    <Table.Row>
                                        <Table.HeaderCell colSpan='2'>{this.props.config.header}</Table.HeaderCell>
                                    </Table.Row>
                                </Table.Header>
                                <Table.Body>
                                    {
                                        data.map(row => {
                                            return (
                                                <Table.Row key={row[Object.keys(row)[0]]}>
                                                    {/* <Table.Cell collapsing>{row[Object.keys(row)[0]] && row[Object.keys(row)[0]].length > 26 ? row[Object.keys(row)[0]].substring(0, 25) + '...' : row[Object.keys(row)[0]]}</Table.Cell>
                                                    <Table.Cell collapsing textAlign='right'>{row[Object.keys(row)[1]] && row[Object.keys(row)[1]].length > 10 ? row[Object.keys(row)[1]].substring(0, 7) + '...' : row[Object.keys(row)[1]]}</Table.Cell> */}
                                                    <div style={{'word-break': 'break-word'}}>
                                                        <Table.Cell width='4'>{row[Object.keys(row)[0]]}</Table.Cell>
                                                    </div>
                                                    <Table.Cell textAlign='right' width='4'>{row[Object.keys(row)[1]]}</Table.Cell>
                                                </Table.Row>
                                            )
                                        }
                                        )}
                                </Table.Body>
                            </Table>

                        </Card.Content>
                        {!footer?null:
                        <Card.Content extra>
                            <div className='ui'>
                                <Label color='green'>{footer} </Label>
                            </div>
                        </Card.Content>}
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
export default connect(mapStateToProps, mapDispatchToProps)(ListWidget);