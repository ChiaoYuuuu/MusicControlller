import React, { Component } from "react";
import { Grid, Button, Typography } from "@material-ui/core";
import { withRouter } from "./utils/withRouter";
import CreateRoomPage from "./CreateRoomPage";
import MusicPlayer from "./MusicPlayer";

function shouldRefreshToken(token) {
  if (!token) return false;
  const payload = JSON.parse(atob(token.split(".")[1]));
  const exp = payload.exp;
  const currentTime = Math.floor(Date.now() / 1000);
  return exp - currentTime < 30;
}

async function refreshAccessToken() {
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
        const payload = JSON.parse(atob(data.access.split(".")[1]));
        console.log("🔐 Refreshed token for user_id:", payload.user_id);
      } else {
        console.warn("Failed to refresh token", data);
      }
      return data;
    })
    .catch((error) => {
      console.error("Refresh token error:", error);
      return null;
    });
}

class Room extends Component {
  constructor(props) {
    super(props);
    this.state = {
      votesToSkip: 2,
      guestCanPause: false,
      isHost: false,
      showSettings: false,
      spotifyAuthenticated: false,
      song: {},
    };
    this.leaveButtonPressed = this.leaveButtonPressed.bind(this);
    this.updateShowSettings = this.updateShowSettings.bind(this);
    this.renderSettingsButton = this.renderSettingsButton.bind(this);
    this.renderSettings = this.renderSettings.bind(this);
    this.getRoomDetails = this.getRoomDetails.bind(this);
    this.getCurrentSong = this.getCurrentSong.bind(this);
    this.authenticateSpotify = this.authenticateSpotify.bind(this);
  }
  componentDidMount() {
    
    this.getRoomDetails();
    this.interval = setInterval(this.getCurrentSong, 1000);
    this.tokenInterval = setInterval(() => {
      const access = localStorage.getItem("access");
      if (shouldRefreshToken(access)) {
        refreshAccessToken();
      }
    }, 1000);
  }

  componentWillUnmount() {
    window.removeEventListener("beforeunload", this.handleUnload);
    clearInterval(this.interval);
    clearInterval(this.tokenInterval);
  }

  handleUnload = (e) => {
    navigator.sendBeacon(
      "/api/auto-leave",
      JSON.stringify({
        room_code: localStorage.getItem("room_code"),
      })
    );

    localStorage.removeItem("room_code");
    //localStorage.removeItem("access");
    //localStorage.removeItem("refresh");
  };

  authenticateSpotify() {
    fetch("/spotify/check-authenticated", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access")}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        this.setState({ spotifyAuthenticated: data.status });
        console.log("authenticateSpotify : ", data.status);

        if (!data.status) {
          fetch("/spotify/get-auth-url", {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${localStorage.getItem("access")}`,
            },
          })
            .then((response) => response.json())
            .then((data) => {
              console.log("AFTER spotify/get-auth-url data.url:", data.url);
              //throw new Error("Room not found");
              window.location.replace(data.url);
            });
        }
      });
  }

  getRoomDetails() {

    const accessToken = localStorage.getItem("access");
    const headers = {
      Authorization: `Bearer ${accessToken}`,
    };
    return fetch("/api/get-room?code=" + this.props.roomCode, {
      headers,
    })
      .then((response) => {
        if (!response.ok) {
          this.props.leaveRoomCallback();
          this.props.navigate("/");
        }
        return response.json();
      })
      .then((data) => {
        this.setState(
          {
            votesToSkip: data.votes_to_skip,
            guestCanPause: data.guest_can_pause,
            isHost: data.is_host,
          },
          () => {
            console.log("👑 Is Host:", data.is_host);
            if (this.state.isHost) {
              this.authenticateSpotify();
            }
          }
        );
      });
  }

  async getCurrentSong() {
    console.log(
      "🎯Room - Current Song Current room_code in localStorage:",
      localStorage.getItem("room_code")
    );
    const accessToken = localStorage.getItem("access");
    const roomCode = localStorage.getItem("room_code");
    console.log("Current Song ROOM CODE : ", roomCode);

    if (shouldRefreshToken(accessToken)) {
      await refreshAccessToken();
      accessToken = localStorage.getItem("access");
    }

    fetch(`/spotify/current-song?room_code=${roomCode}`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
    })
      .then((response) => {
        if (!response.ok || response.status === 204) {
          console.log("Get Current Song faild");
          return {};
        } else {
          console.log("Get Current Song success");
          return response.json();
        }
      })
      .then((data) => {
        this.setState({ song: data });
        //console.log("Get Current : ", data);
      });
  }

  leaveButtonPressed() {
    const requestOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access")}`,
      },
    };
    fetch("/api/leave-room", requestOptions).then((_response) => {
      console.log("Leave");
      localStorage.removeItem("room_code");
      this.props.navigate("/");
    });
  }

  updateShowSettings(value) {
    this.setState({
      showSettings: value,
    });
  }

  renderSettings() {
    return (
      <Grid container spacing={1}>
        <Grid item xs={12} align="center">
          <CreateRoomPage
            update={true}
            votesToSkip={this.state.votesToSkip}
            guestCanPause={this.state.guestCanPause}
            roomCode={this.props.roomCode}
            updateCallback={this.getRoomDetails}
          />
        </Grid>
        <Grid item xs={12} align="center">
          <Button
            variant="contained"
            color="secondary"
            onClick={() => this.updateShowSettings(false)}
          >
            Close
          </Button>
        </Grid>
      </Grid>
    );
  }

  renderSettingsButton() {
    return (
      <Grid item xs={12} align="center">
        <Button
          variant="contained"
          color="primary"
          onClick={() => this.updateShowSettings(true)}
        >
          Settings
        </Button>
      </Grid>
    );
  }

  render() {
    //console.log("ROOM Render");
    if (this.state.showSettings) {
      return this.renderSettings();
    }
    return (
      <Grid container spacing={1}>
        <Grid item xs={12} align="center">
          <Typography variant="h4" component="h4">
            Code: {this.props.roomCode}
          </Typography>
        </Grid>
        <MusicPlayer {...this.state.song} />
        {this.state.isHost ? this.renderSettingsButton() : null}
        <Grid item xs={12} align="center">
          <Button
            variant="contained"
            color="secondary"
            onClick={this.leaveButtonPressed}
          >
            Leave Room
          </Button>
        </Grid>
      </Grid>
    );
  }
}
export default withRouter(Room);
