// Logout.js
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("username");
    localStorage.removeItem("password");
    localStorage.removeItem("room_code");

    window.location.href = "/";
  }, [navigate]);

  return null;
}

export default Logout;
