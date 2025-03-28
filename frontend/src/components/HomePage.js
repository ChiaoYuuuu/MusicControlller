import React, { Component } from "react";
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Room from "./Room";
import { Grid, Button, ButtonGroup, Typography } from "@material-ui/core";
import { Link, useParams, Navigate } from "react-router-dom";
import Info from "./info";


function RoomWrapper(props){
  let { roomCode } = useParams();
  return <Room {...props} roomCode={roomCode} />;
};


export default class HomePage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      roomCode: null,
    };
    this.clearRoomCode = this.clearRoomCode.bind(this);
  }

  async componentDidMount() {
    fetch("/api/user-in-room")
      .then((response) => response.json())
      .then((data) => {
        this.setState({
          roomCode: data.code,
        });
      });
  }

  renderHomePage() {
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} align="center">
          <Typography variant="h3" compact="h3">
            House Party
          </Typography>
        </Grid>
        <Grid item xs={12} align="center">
          <ButtonGroup disableElevation variant="contained" color="primary">
            <Button color="primary" to="/join" component={Link}>
              Join a Room
            </Button>
            <Button color="default" to="/info" component={Link}>
              Info
            </Button>           
            <Button color="secondary" to="/create" component={Link}>
              Create a Room
            </Button>
          </ButtonGroup>
        </Grid>
      </Grid>
    );
  }

  clearRoomCode() {
    this.setState({
      roomCode: null,
    });
  }


  render() {
    return (
      <div className="center">
        <Router>
          <Routes>
            <Route path="/" element={this.state.roomCode ? (
              <Navigate to={`/room/${this.state.roomCode}`} /> ) : (this.renderHomePage()
            )} />
            <Route path="/join/*" element={<RoomJoinPage />} />
            <Route path="/info/" element={<Info />} />
            <Route path="/create/*" element={<CreateRoomPage />} />
            <Route path="/room/:roomCode" element={<RoomWrapper leaveRoomCallback={this.clearRoomCode} />} />
          </Routes>
        </Router>
      </div>
    );
  }
}



