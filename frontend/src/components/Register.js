import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const register = async () => {
    try {
      const res = await axios.post(
        "/api/register",
        { username, password },
        { headers: { "Content-Type": "application/json" } }
      );
      alert("Registration successful!");
      localStorage.setItem("access", res.data.access);
      localStorage.setItem("refresh", res.data.refresh);
      window.location.href = "/";
    } catch (err) {
      alert(
        "Registration failed: " + (err.response?.data?.error || err.message)
      );
    }
  };

  return (
    <div style={{ textAlign: "center" }}>
      <h2>Register</h2>
      <input
        placeholder="Username"
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={register}>Register</button>

      <div style={{ marginTop: "20px" }}>
        <button onClick={() => navigate("/", { replace: true })}>
          Back to Home
        </button>
      </div>
    </div>
  );
}

export default Register;
