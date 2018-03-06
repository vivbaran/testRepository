import React, { Component } from 'react';
import { Card, Image, Label } from 'semantic-ui-react'

import { connect } from 'react-redux';

import {
    APPS_ITEM_SELECTED
} from '../../constants/actionTypes';


const mapStateToProps = state => ({
    ...state.apps
});

const mapDispatchToProps = dispatch => ({
    selectAppItem: (payload) =>
        dispatch({ type: APPS_ITEM_SELECTED, payload })
});



class AppList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            apps: undefined
        }
    }

    onCardClicked(event, param) {
        this.props.selectAppItem(param.app);
    }
    
    componentWillReceiveProps(nextProps) {
        this.setState({
            apps: undefined,
            scopeExposure: nextProps.scopeExposure
        })
    }

    render() {
        var appCards =[]
        if (this.props.appPayLoad) {
            let allapps = []
            if (this.state.scopeExposure === 0)
            {
                allapps =this.props.appPayLoad
            }
            else
            {
                for(let appkey in this.props.appPayLoad)
                {
                    let app = this.props.appPayLoad[appkey]
                    if (this.state.scopeExposure === 2 && !app.is_readonly_scope)
                        allapps.push(app)
                    else if (this.state.scopeExposure === 1 && app.is_readonly_scope)
                        allapps.push(app)
                }
            }
            for(let appkey in allapps)
            {
                var app = allapps[appkey]
                var appName = app.display_text;
                var image = <Image key={appkey} floated='right' size='tiny' ><Label style={{ fontSize: '1.2rem' }} circular >{appName.charAt(0)}</Label></Image>
                
                appCards.push(<Card key={appkey}  app={app} onClick={this.onCardClicked.bind(this)} color={this.props.selectedAppItem && this.props.selectedAppItem.key === appName?'blue':'grey'}>
                    <Card.Content>
                        {image}
                        <Card.Header>
                            {appName}
                        </Card.Header>
                    </Card.Content>
                </Card>)
            }
        }
        return (
            <Card.Group style={{ maxHeight: document.body.clientHeight, overflow: "auto" }}>
                {appCards}
            </Card.Group>

        )

    }
}

export default connect(mapStateToProps, mapDispatchToProps)(AppList);