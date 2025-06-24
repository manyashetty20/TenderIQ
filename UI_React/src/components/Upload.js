import React, { useState } from "react";
import axios from "axios";
import "./Upload.css";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [meta, setMeta] = useState({ vendor: "", type: "", date: "" });

  const handleUpload = async () => {
    if (!file) return alert("Choose a file first!");
    const formData = new FormData();
    formData.append("file", file);
    Object.entries(meta).forEach(([k, v]) => formData.append(k, v));

    try {
      await axios.post("/api/upload", formData);
      alert("Uploaded successfully!");
      setFile(null);
      setMeta({ vendor: "", type: "", date: "" });
    } catch (err) {
      alert("Upload failed");
    }
  };

  return (
    <div className="upload__wrapper">
      <h2>Upload Hospital Document</h2>
      <div className="upload__card">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <input
          placeholder="Vendor Name"
          value={meta.vendor}
          onChange={(e) => setMeta({ ...meta, vendor: e.target.value })}
        />
        <input
          placeholder="Document Type"
          value={meta.type}
          onChange={(e) => setMeta({ ...meta, type: e.target.value })}
        />
        <input
          type="date"
          value={meta.date}
          onChange={(e) => setMeta({ ...meta, date: e.target.value })}
        />
        <button onClick={handleUpload}>Upload</button>
      </div>
    </div>
  );
}
