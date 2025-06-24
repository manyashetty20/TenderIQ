import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

export default function Login() {
  const [token, setToken] = useState("");
  const navigate = useNavigate();

  const handleLogin = () => {
    if (token.trim()) {
      localStorage.setItem("userToken", token);
      navigate("/dashboard");
    }
  };

  return (
    <div className="login__wrapper">
      <div className="login__card">
        <h2>Hospital Portal Login</h2>
        <input
          placeholder="Enter Access Token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
        />
        <button onClick={handleLogin}>Login</button>
      </div>
    </div>
  );
}
