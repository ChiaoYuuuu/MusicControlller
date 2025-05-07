import React, { Component } from "react";
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Room from "./Room";
import { Grid, Button, ButtonGroup, Typography } from "@material-ui/core";
import { Link, useParams, Navigate } from "react-router-dom";
import Info from "./info";
import Register from "./Register";
import Login from "./Login";
import Logout from "./Logout";
import SpotifyConflict from "./SpotifyConflict";
import RoomCheckPage from "./RoomCheckPage";
import TopCharts from "./TopCharts";

function RoomWrapper(props) {
  const { roomCode } = useParams();
  return <Room {...props} roomCode={roomCode} />;
}

function shouldRefreshToken(token) {
  if (!token) return false;
  const payload = JSON.parse(atob(token.split(".")[1]));
  const exp = payload.exp;
  const currentTime = Math.floor(Date.now() / 1000);
  return exp - currentTime < 30;
}

function refreshAccessToken() {
  const refresh = localStorage.getItem("refresh");

  fetch("/api/token-refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: refresh }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.access) {
        localStorage.setItem("access", data.access);
        console.log("JWT token refreshed");
      } else {
        console.warn("Failed to refresh token", data);
      }
    })
    .catch((error) => {
      console.error("Refresh token error:", error);
    });
}

export default class HomePage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isAuthenticated: !!localStorage.getItem("access"),
      roomCode: "",
      loading: true,
    };
    this.clearRoomCode = this.clearRoomCode.bind(this);
    this.renderHomePage = this.renderHomePage.bind(this);
    console.log("constructor access : ", localStorage.getItem("access"));
  }

  async componentDidMount() {
    const accessToken = localStorage.getItem("access");

    if (accessToken) {
      const requestOptions = {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
      };

      try {
        const response = await fetch("/api/user-in-room", requestOptions);
        const data = await response.json();
        console.log("🎯 Got room code from API:", data.code);
        localStorage.setItem("room_code", data.code);

        console.log("/api/user-in-room : isAuthenticated: true");
        this.setState({
          isAuthenticated: true,
          roomCode: data.code,
          loading: false,
        });
      } catch (err) {
        console.warn("User not in room or API failed:", err);
        console.log("/api/user-in-room : isAuthenticated: ", true);
        this.setState({
          isAuthenticated: true,
          roomCode: "",
          loading: false,
        });
      }
    } else {
      console.log(
        "/api/user-in-room  accessToken FAILED : isAuthenticated: false"
      );
      this.setState({
        isAuthenticated: false,
        roomCode: "",
        loading: false,
      });
    }

    this.tokenInterval = setInterval(() => {
      const access = localStorage.getItem("access");
      if (shouldRefreshToken(access)) {
        refreshAccessToken();
      }
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.tokenInterval);
  }

  renderHomePage() {
    console.log("Render Home : ", this.state.isAuthenticated);
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} align="center">
          <Typography variant="h3" compact="h3">
            Spotify Controller
          </Typography>
        </Grid>
        <Grid item xs={12} align="center">
          {this.state.isAuthenticated ? (
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
              <Button color="default" to="/logout" component={Link}>
                Logout
              </Button>
            </ButtonGroup>
          ) : (
            <>
              <Button color="primary" to="/login" component={Link}>
                Login
              </Button>
              <Button color="secondary" to="/register" component={Link}>
                Register
              </Button>
            </>
          )}
          <Grid item xs={12}>
            <TopCharts />
          </Grid>
        </Grid>
      </Grid>
    );
  }

  clearRoomCode() {
    localStorage.removeItem("room_code");
  }

  render() {
    console.log("render home");
    console.log("current path:", window.location.pathname);
    console.log("state roomcode: ", this.state.roomCode);
    console.log("state loading: ", this.state.loading);
    //throw new Error("Room not found");
    return (
      <div className="center">
        <Router>
          <Routes>
            <Route
              path="/"
              element={
                this.state.loading ? (
                  <div>Loading...</div>
                ) : this.state.roomCode &&
                  this.state.roomCode !== "null" &&
                  this.state.roomCode !== "undefined" &&
                  this.state.roomCode !== "" ? (
                  <Navigate to={`/room/${this.state.roomCode}`} />
                ) : (
                  this.renderHomePage()
                )
              }
            />

            {this.state.loading ? null : (
              <Route
                path="/room/:roomCode"
                element={
                  <RoomWrapper
                    leaveRoomCallback={this.clearRoomCode}
                    roomCodeFromState={this.state.roomCode}
                  />
                }
              />
            )}

            <Route path="/room-check/:roomCode" element={<RoomCheckPage />} />
            <Route path="/join/*" element={<RoomJoinPage />} />
            <Route path="/info/" element={<Info />} />
            <Route path="/create/*" element={<CreateRoomPage />} />
            <Route path="/register/" element={<Register />} />
            <Route path="/login/" element={<Login />} />
            <Route path="/logout/" element={<Logout />} />
            <Route path="/spotify-conflict/" element={<SpotifyConflict />} />
          </Routes>
        </Router>
      </div>
    );
  }
}
//ROUTE下半段 :
//<Route
//path="/room/:roomCode"
//element={<RoomWrapper leaveRoomCallback={this.clearRoomCode} />}
///>
