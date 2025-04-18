import React from "react";

function SpotifyConflict() {
  console.log("SpotifyConflict");
  const handleSwitchSpotify = () => {
    const refresh = localStorage.getItem("refresh");

    if (!refresh) {
      alert("No refresh token found. Please log in again.");
      return;
    }
    console.log("SpotifyConflict");
    throw new Error("Room not found");
    // 先刷新 access token
    fetch("/api/token-refresh", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh: refresh }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.access) {
          localStorage.setItem("access", data.access);
          console.log("✅ New access token refreshed");

          // 然後取得 Spotify 授權網址
          fetch("/spotify/get-auth-url", {
            headers: {
              Authorization: `Bearer ${data.access}`,
            },
          })
            .then((response) => response.json())
            .then((data) => {
              // 導向 Spotify 授權頁，強制出現 Not you?
              window.location.replace(data.url);
            });
        } else {
          alert("❌ Failed to refresh token. Please log in again.");
        }
      })
      .catch((err) => {
        console.error("Error refreshing access token", err);
        alert("Something went wrong. Please log in again.");
      });
  };

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h2>This Spotify account is already linked to another user.</h2>
      <p>Please switch to a different Spotify account.</p>
      <button onClick={handleSwitchSpotify}>Switch Spotify Account</button>
    </div>
  );
}

export default SpotifyConflict;
