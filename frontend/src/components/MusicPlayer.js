import React, { Component } from "react";
import {
  Grid,
  Typography,
  Card,
  IconButton,
  LinearProgress,
} from "@material-ui/core";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import PauseIcon from "@material-ui/icons/Pause";
import SkipNextIcon from "@material-ui/icons/SkipNext";
import SkipPreviousIcon from "@material-ui/icons/SkipPrevious";

export default class MusicPlayer extends Component {
  constructor(props) {
    super(props);
  }

  skipSong() {
    const accessToken = localStorage.getItem("access");
    const roomCode = localStorage.getItem("room_code");
    const requestOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ room_code: roomCode }),
    };
    fetch("/spotify/skip", requestOptions)
      .then((response) => {
        if (response.status === 204) {
          console.log("Skip successfully.");
        } else if (response.status === 403) {
          console.log("Not allowed to skip.");
        } else {
          console.log("Failed to skip.");
        }
      })
      .catch((err) => {
        console.error("Error in skipSong:", err);
      });
  }

  previouSong() {
    const accessToken = localStorage.getItem("access");
    const roomCode = localStorage.getItem("room_code");
    const requestOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ room_code: roomCode }),
    };
    fetch("/spotify/previous", requestOptions)
      .then((response) => {
        if (response.status === 204) {
          console.log("Previous successfully.");
        } else if (response.status === 403) {
          console.log("Changing to a previous one is not allowed.");
        } else {
          console.log("Unable to change to previous one.");
        }
      })
      .catch((err) => {
        console.error("Error in previousSong:", err);
      });
  }

  pauseSong() {
    const accessToken = localStorage.getItem("access");
    const roomCode = localStorage.getItem("room_code");
    const requestOptions = {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ room_code: roomCode }),
    };
    fetch("/spotify/pause", requestOptions)
      .then((response) => {
        if (response.status === 204) {
          console.log("Paused successfully.");
        } else if (response.status === 403) {
          console.log("Not allowed to pause.");
        } else {
          console.log("Failed to pause.");
        }
      })
      .catch((err) => {
        console.error("Error in pauseSong:", err);
      });
  }

  playSong() {
    const accessToken = localStorage.getItem("access");
    const roomCode = localStorage.getItem("room_code");
    const requestOptions = {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ room_code: roomCode }),
    };
    fetch("/spotify/play", requestOptions)
      .then((response) => {
        if (response.status === 204) {
          console.log("Play successfully.");
        } else if (response.status === 403) {
          console.log("Not allowed to play.");
        } else {
          console.log("Failed to play.");
        }
      })
      .catch((err) => {
        console.error("Error in playSong:", err);
      });
  }

  render() {
    const songProgress = (this.props.time / this.props.duration) * 100;

    return (
      <Card>
        <Grid container alignItems="center">
          <Grid item align="center" xs={4}>
            <img src={this.props.image_url} height="100%" width="100%" />
          </Grid>
          <Grid item align="center" xs={8}>
            <Typography component="h5" variant="h5">
              {this.props.title}
            </Typography>
            <Typography color="textSecondary" variant="subtitle1">
              {this.props.artist}
            </Typography>
            <div>
              <IconButton onClick={() => this.previouSong()}>
                <SkipPreviousIcon /> {this.props.previous_votes ?? 0} /{" "}
                {this.props.votes_required ?? 0}
              </IconButton>
              <IconButton
                onClick={() => {
                  this.props.is_playing ? this.pauseSong() : this.playSong();
                }}
              >
                {this.props.is_playing ? <PauseIcon /> : <PlayArrowIcon />}
              </IconButton>
              <IconButton onClick={() => this.skipSong()}>
                <SkipNextIcon /> {this.props.skip_votes ?? 0} /{" "}
                {this.props.votes_required ?? 0}
              </IconButton>
            </div>
          </Grid>
        </Grid>
        <LinearProgress variant="determinate" value={songProgress} />
      </Card>
    );
  }
}
