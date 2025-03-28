import { useParams } from "react-router-dom";
import Room from "./Room";
import React from "react";

function RoomWrapper(props) {
    let { roomCode } = useParams();
    return <Room {...props} roomCode={roomCode} />;
}

export default RoomWrapper;
