import React, { Component } from 'react'
import { Form }  from 'semantic-ui-react'
import { connect } from 'react-redux';



const mapStateToProps = state => ({
    logged_in_user : state.common.currentUser,
    all_actions_list: state.common.all_actions_list,
    //action: this.props.isUserAction ? state.users.action : state.resources.action,
    selectedUser: state.users.selectedUserItem
});

const mapDispatchToProps = dispatch => ({

});

class ActionsFormInput extends Component {
  constructor(props) {
    super(props);
    this.state = {
      rows : [],

    }
  }

  translate_param_to_label(param) {
    if (param === "old_owner_email")
      return "File Owner: ";
    else if(param === "new_owner_email")
      return "To User: ";
    else if(param === "resource_id")
      return "For File Name: ";
    else if (param === 'user_email')
      return "For User: ";
    else if (param === "new_permission_role") {
      return "Change permission to: ";
    }
    else return param;
  }


  constructRows() {
    const rows = [];
    let parameters = this.props.getActionParameters(false);
    console.log("found parameters in input: ")
    console.log(parameters)
    let parameters_map = {};
    for ( let param of Object.keys(parameters)) {
      let label = this.translate_param_to_label(param);
      let placeholder = "";
      if (this.props.isUserAction === true) {
        placeholder = (param === "old_owner_email"|| param === "user_email") ? this.props.selectedUser.key : "";
      }
      else {
        if(param === "old_owner_email" || param === "resource_owner_id")
          placeholder= this.props.rowData["resource_owner_id"];
        else if(param === "resource_id")
          placeholder = this.props.rowData["resource_name"]
        else if (param === "user_email")
          placeholder = this.props.action["actionEmail"]
        else if (param === "new_permission_role")
          placeholder = this.props.action["actionNewValue"];

      }

      let readOnly = (param === "old_owner_email"
                    || param === "user_email"
                    || param === "resource_id"
                    || param === "resource_owner_id"
                    || param === "new_permission_role") ? true : false;
      parameters_map[param] = "";

      if (readOnly === true) {
        if(param === "resource_id") {
          parameters_map[param] = this.props.rowData["resource_id"];
        }
        else if(param === "resource_owner_id") {
          parameters_map[param] = this.props.rowData["resource_owner_id"];

        }
        else if(param === "new_permission_role") {
          let role = this.props.action["actionNewValue"];
          if (role === "Read")
            role = "reader";
          else if(role === "Write")
            role = "writer";
          parameters_map[param] = role;
        }
        else {
          parameters_map[param] = placeholder;
          }
        this.props.updateState("parameters_map", parameters_map);

      }


      rows.push(<Form.Input fluid label={label}
        key = {param}
        onChange={(e) => { parameters_map[param] = e.target.value;
            this.props.updateState("parameters_map", parameters_map)}}

        placeholder={placeholder}
        readOnly={readOnly} />)


      this.props.updateState(parameters_map, parameters_map);

    }
    return rows;
  }

  componentDidMount() {
    console.log("in modal: ")
    console.log(this.props.action)
    this.setState({rows: this.constructRows()});
    //this.setState({rows: [] });

  }

  componentWillUnmount() {
    this.setState({rows: []});

  }


  render() {

    return (
        this.state.rows
      )

  }
}





export default connect(mapStateToProps, mapDispatchToProps)(ActionsFormInput);
