import React from "react";
import { Link } from "react-router-dom";
import "./Dashboard.css";

export default function Dashboard() {
  return (
    <div className="dash__wrapper">
      <h1>Welcome to the Hospital Library</h1>
      <div className="dash__buttons">
        <Link to="/upload" className="dash-btn">
          📤 Upload Document
        </Link>
        <Link to="/search" className="dash-btn">
          🔍 Search Documents
        </Link>
      </div>
    </div>
  );
}
