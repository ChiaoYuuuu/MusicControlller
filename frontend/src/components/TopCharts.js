import React, { useEffect, useState } from "react";

function TopCharts() {
  const [charts, setCharts] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState("TW");

  useEffect(() => {
    fetch("/api/top-song")
      .then((res) => res.json())
      .then((data) => {
        console.log("🎵 Charts data from backend:", data);
        setCharts(data);
      })
      .catch((err) => console.error("Failed to load charts:", err));
  }, []);

  if (!charts) return <p>Loading charts...</p>;

  const countries = Object.keys(charts);

  return (
    <div style={{ marginTop: "30px", textAlign: "center" }}>
      <h3>Top 10 Songs by Country</h3>
      <select
        value={selectedCountry}
        onChange={(e) => setSelectedCountry(e.target.value)}
        style={{
          padding: "8px",
          marginBottom: "20px",
          fontSize: "16px",
          borderRadius: "5px",
        }}
      >
        {countries.map((country) => (
          <option key={country} value={country}>
            {country}
          </option>
        ))}
      </select>

      <div
        style={{
          maxHeight: "200px",
          width: "50%",
          margin: "0 auto",
          border: "1px solid white",
          borderRadius: "8px",
          backgroundColor: "#222",
          overflowY: "auto",
          padding: "16px",
        }}
      >
       
        <ol style={{ color: "white", paddingLeft: "20px" }}>
          {charts[selectedCountry].map((song, index) => (
            <li key={index}>
              {song.song_name} - {song.artist_name}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}

export default TopCharts;



