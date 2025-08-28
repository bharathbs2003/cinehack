import { useState } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import "./App.css";

export default function App() {
  const [video, setVideo] = useState(null);
  const [language, setLanguage] = useState("hi");
  const [loading, setLoading] = useState(false);
  const [dubbedVideo, setDubbedVideo] = useState(null);

  const API_BASE = "http://localhost:8000";

  const handleUpload = (e) => {
    setVideo(e.target.files[0]);
    setDubbedVideo(null);
  };

  const handleDub = async () => {
    if (!video) return alert("Upload a video first!");
    setLoading(true);

    const formData = new FormData();
    formData.append("file", video);
    formData.append("lang", language);

    try {
      const res = await axios.post(`${API_BASE}/dub`, formData, {
        responseType: "blob",
      });

      const videoUrl = URL.createObjectURL(res.data);
      setDubbedVideo(videoUrl);
    } catch (err) {
      console.error("Dubbing failed:", err);
      alert("⚠️ Dubbing failed! Check console.");
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      {/* Hero Section */}
      <motion.section
        className="hero-section"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <h1 className="hero-title">🎙 EduDub Live</h1>
        <p className="hero-subtitle">
          Instantly dub your videos into 20+ languages with high-quality AI voices. 
          Perfect for education, content creators, and multilingual audiences.
        </p>
      </motion.section>

      {/* Upload Card */}
      <motion.div
        className="upload-card"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
      >
        <label className="file-upload">
          <div className={`upload-box ${video ? "uploaded" : ""}`}>
            {video ? `🎬 ${video.name}` : "Upload your video"}
          </div>
          <input type="file" accept="video/*" onChange={handleUpload} />
        </label>

        <select
          className="language-select"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option value="en">English</option>
          <option value="hi">Hindi</option>
          <option value="mr">Marathi</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
          <option value="it">Italian</option>
          <option value="pt">Portuguese</option>
          <option value="ru">Russian</option>
          <option value="zh">Chinese</option>
          <option value="ja">Japanese</option>
          <option value="ko">Korean</option>
          <option value="ar">Arabic</option>
          <option value="tr">Turkish</option>
          <option value="bn">Bengali</option>
          <option value="pa">Punjabi</option>
          <option value="ta">Tamil</option>
          <option value="te">Telugu</option>
          <option value="ur">Urdu</option>
          <option value="vi">Vietnamese</option>
          <option value="th">Thai</option>
        </select>

        <motion.button
          onClick={handleDub}
          disabled={loading}
          className={`dub-btn ${loading ? "loading" : ""}`}
          whileTap={{ scale: 0.95 }}
        >
          {loading ? "Processing..." : "Generate Dubbed Video"}
        </motion.button>

        {dubbedVideo && (
          <motion.div
            className="video-preview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h2>📽 Dubbed Video</h2>
            <video src={dubbedVideo} controls />
            <a href={dubbedVideo} download="dubbed.mp4">
              ⬇️ Download Dubbed Video
            </a>
          </motion.div>
        )}
      </motion.div>

      {/* Footer */}
      <footer className="app-footer">
        &copy; 2025 EduDub Live. All rights reserved.
      </footer>
    </div>
  );
}
