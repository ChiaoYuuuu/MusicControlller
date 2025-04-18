import React, { useEffect } from "react";
import { useParams } from "react-router-dom";

export default function RoomCheckPage() {
  const { roomCode } = useParams();
  const localRoomCode = localStorage.getItem("room_code");

  useEffect(() => {
    console.log("🟢 URL 參數 roomCode:", roomCode);
    console.log("🟡 localStorage room_code:", localRoomCode);
  }, [roomCode]);

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h2>🔍 Room Check Page</h2>
      <p>
        Room code from URL: <strong>{roomCode}</strong>
      </p>
      <p>
        Room code from localStorage: <strong>{localRoomCode}</strong>
      </p>
    </div>
  );
}
