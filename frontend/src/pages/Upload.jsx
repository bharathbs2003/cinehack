import { useState } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import UploadNavbar from "../components/UploadNavbar";
import VoiceWave from "../components/VoiceWave.jsx";
import Footer from "../components/Footer.jsx";
import "../Upload.css";

export default function Upload() {
  const [video, setVideo] = useState(null);
  const [language, setLanguage] = useState("hi");
  const [loading, setLoading] = useState(false);
  const [dubbedVideo, setDubbedVideo] = useState(null);

  const API_BASE = "http://localhost:8000";

  const handleUpload = (e) => setVideo(e.target.files[0]);

  const handleDub = async () => {
    if (!video) return alert("Upload a video first!");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", video);
    formData.append("lang", language);

    try {
      const res = await axios.post(`${API_BASE}/dub`, formData, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      setDubbedVideo(url);
    } catch (err) {
      console.error(err);
      alert("⚠️ Dubbing failed!");
    }
    setLoading(false);
  };

  return (
    <div className="upload-page">
      <UploadNavbar />
      <motion.div className="upload-modal" initial={{ scale:0.9, opacity:0 }} animate={{ scale:1, opacity:1 }} transition={{ duration:0.7 }}>
        <h2>🎬 Upload & Dub</h2>
        <label className="file-upload">
          <input type="file" accept="video/*" onChange={handleUpload} />
          <div className={`upload-box ${video ? "uploaded" : ""}`}>
            {video ? `✅ ${video.name}` : "Choose a video"}
          </div>
        </label>

        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="hi">Hindi</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
        </select>

        <motion.button className="dub-btn" whileTap={{ scale: 0.95 }} onClick={handleDub} disabled={loading}>
          {loading ? "⏳ Processing..." : "🎙 Generate Dub"}
        </motion.button>

        <VoiceWave loading={loading} />

        {dubbedVideo && (
          <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ duration:0.6 }} className="video-preview">
            <h3>📽 Preview</h3>
            <video src={dubbedVideo} controls />
            <a href={dubbedVideo} download="dubbed.mp4">⬇️ Download</a>
          </motion.div>
        )}
      </motion.div>
      <Footer />
    </div>
  );
}

