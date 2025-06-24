import React from "react";
import "./ResultCard.css";

export default function ResultCard({ result }) {
  return (
    <div className="card">
      <h3>{result.title}</h3>
      <p>{result.snippet}</p>
      <div className="meta">
        Vendor: {result.vendor} &nbsp;|&nbsp; Date: {result.date}
      </div>
      <a href={result.download_url} target="_blank" rel="noreferrer">
        📄 View Document
      </a>
    </div>
  );
}
