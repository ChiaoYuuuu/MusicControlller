import React, { Component } from "react";
import { TextField, Button, Grid, Typography } from "@material-ui/core";
import { Link } from "react-router-dom";
import { withRouter } from "./utils/withRouter";

class RoomJoinPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      roomCode: "",
      error: "",
    };
    this.handleTextFieldChange = this.handleTextFieldChange.bind(this);
    this.roomButtonPressed = this.roomButtonPressed.bind(this);
  }

  handleTextFieldChange(e) {
    this.setState({
      roomCode: e.target.value,
      error: "",
    });
  }

  roomButtonPressed() {
    const accessToken = localStorage.getItem("access");
    const requestOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ code: this.state.roomCode }),
    };
    fetch("/api/join-room", requestOptions)
      .then((response) => {
        if (response.ok) {
          console.log("Room Join Room Code : ", this.state.roomCode);
          localStorage.setItem("room_code", this.state.roomCode);
          if (this.state.roomCode && this.state.roomCode !== "undefined") {
            console.log("222222222222 room : ", this.state.roomCode);
            this.props.navigate(`/room/${this.state.roomCode}`);
          }
        } else {
          this.setState({ error: "Room not found." });
        }
      })
      .catch((error) => console.error(error));
  }

  render() {
    return (
      <Grid container spacing={1}>
        <Grid item xs={12} align="center">
          <Typography variant="h4">Join a Room</Typography>
        </Grid>
        <Grid item xs={12} align="center">
          <TextField
            error={this.state.error !== ""}
            label="Code"
            placeholder="Enter a Room Code"
            value={this.state.roomCode}
            helperText={this.state.error}
            variant="outlined"
            onChange={this.handleTextFieldChange}
          />
        </Grid>
        <Grid item xs={12} align="center">
          <Button
            variant="contained"
            color="primary"
            onClick={this.roomButtonPressed}
          >
            Enter Room
          </Button>
        </Grid>
        <Grid item xs={12} align="center">
          <Button variant="contained" color="secondary" to="/" component={Link}>
            Back
          </Button>
        </Grid>
      </Grid>
    );
  }
}

export default withRouter(RoomJoinPage);
