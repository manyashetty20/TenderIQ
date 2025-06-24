import React, { useState } from "react";
import axios from "axios";
import ResultCard from "./ResultCard";
import "./Search.css";

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    try {
      const res = await axios.post("/api/search", { query });
      setResults(res.data.results);
    } catch {
      alert("Search failed – check backend.");
    }
  };

  return (
    <div className="search__wrapper">
      <h2>AI‑Powered Hospital Search</h2>
      <div className="search__box">
        <input
          placeholder="Search medical reports, SOPs..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      <div className="search__results">
        {results.map((r, i) => (
          <ResultCard key={i} result={r} />
        ))}
      </div>
    </div>
  );
}
