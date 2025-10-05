import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import UploadNavbar from "../components/UploadNavbar";
import VoiceWave from "../components/VoiceWave.jsx";
import Footer from "../components/Footer.jsx";
import "../Upload.css";

export default function UploadV2() {
  const [video, setVideo] = useState(null);
  const [targetLanguage, setTargetLanguage] = useState("hi");
  const [sourceLanguage, setSourceLanguage] = useState("en");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState("idle");
  const [message, setMessage] = useState("Upload a video to get started");
  const [dubbedVideo, setDubbedVideo] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [transcript, setTranscript] = useState(null);
  
  // Advanced options
  const [useWhisperX, setUseWhisperX] = useState(true);
  const [useDiarization, setUseDiarization] = useState(true);
  const [useEmotion, setUseEmotion] = useState(true);
  const [useElevenLabs, setUseElevenLabs] = useState(false);
  const [useWav2Lip, setUseWav2Lip] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const languages = [
    { code: "en", name: "English" },
    { code: "hi", name: "Hindi" },
    { code: "es", name: "Spanish" },
    { code: "fr", name: "French" },
    { code: "de", name: "German" },
    { code: "zh", name: "Chinese" },
    { code: "ja", name: "Japanese" },
    { code: "ko", name: "Korean" },
    { code: "ar", name: "Arabic" },
    { code: "pt", name: "Portuguese" },
    { code: "ru", name: "Russian" },
    { code: "it", name: "Italian" },
    { code: "mr", name: "Marathi" },
    { code: "bn", name: "Bengali" },
    { code: "ta", name: "Tamil" },
    { code: "te", name: "Telugu" }
  ];

  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setVideo(file);
      setMessage(`Selected: ${file.name}`);
    }
  };

  const pollJobStatus = async (jId, tId) => {
    try {
      const statusRes = await axios.get(`${API_BASE}/api/v2/status/${jId}?task_id=${tId}`);
      const { status, progress: prog, stage: stg, message: msg, result } = statusRes.data;

      setStage(stg || status);
      setProgress(prog || 0);
      setMessage(msg || `Status: ${status}`);

      if (status === "success") {
        // Fetch result video
        const videoRes = await axios.get(`${API_BASE}/api/v2/result/${jId}`, {
          responseType: "blob",
        });
        const url = URL.createObjectURL(videoRes.data);
        setDubbedVideo(url);
        
        // Fetch transcript
        try {
          const transcriptRes = await axios.get(`${API_BASE}/api/v2/transcript/${jId}`);
          setTranscript(transcriptRes.data);
        } catch (e) {
          console.log("Transcript not available yet");
        }
        
        setLoading(false);
        setMessage("✅ Dubbing complete!");
      } else if (status === "failure") {
        setMessage(`❌ Error: ${statusRes.data.error || "Processing failed"}`);
        setLoading(false);
      } else {
        // Continue polling
        setTimeout(() => pollJobStatus(jId, tId), 3000);
      }
    } catch (err) {
      console.error(err);
      setMessage("⚠️ Error checking status!");
      setLoading(false);
    }
  };

  const handleDub = async () => {
    if (!video) return alert("Please upload a video first!");
    
    setLoading(true);
    setProgress(0);
    setStage("uploading");
    setMessage("Uploading video...");
    setDubbedVideo(null);
    setTranscript(null);

    const formData = new FormData();
    formData.append("file", video);
    formData.append("target_language", targetLanguage);
    formData.append("source_language", sourceLanguage);
    formData.append("use_whisperx", useWhisperX);
    formData.append("use_diarization", useDiarization);
    formData.append("use_emotion", useEmotion);
    formData.append("use_elevenlabs", useElevenLabs);
    formData.append("use_wav2lip", useWav2Lip);

    try {
      const res = await axios.post(`${API_BASE}/api/v2/dub`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      const { job_id, task_id } = res.data;
      setJobId(job_id);
      setTaskId(task_id);
      setMessage("Processing started...");
      setStage("queued");
      
      // Start polling
      pollJobStatus(job_id, task_id);
    } catch (err) {
      console.error(err);
      setMessage(`⚠️ Upload failed: ${err.response?.data?.detail || err.message}`);
      setLoading(false);
    }
  };

  const getStageDescription = (stg) => {
    const stages = {
      idle: "Ready to start",
      uploading: "Uploading video...",
      queued: "In queue...",
      init: "Initializing...",
      extract_audio: "Extracting audio...",
      transcribe: "Transcribing speech...",
      diarization: "Identifying speakers...",
      emotion: "Detecting emotions...",
      translate: "Translating text...",
      voice_generation: "Generating voices...",
      audio_merge: "Merging audio...",
      lipsync: "Applying lip-sync...",
      complete: "Complete!",
      error: "Error occurred"
    };
    return stages[stg] || stg;
  };

  const downloadTranscript = () => {
    if (!transcript) return;
    const blob = new Blob([JSON.stringify(transcript, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transcript_${jobId}.json`;
    a.click();
  };

  return (
    <div className="upload-page">
      <UploadNavbar />
      <motion.div
        className="upload-modal"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.7 }}
      >
        <h2>🎬 Advanced Video Dubbing</h2>
        
        {/* File Upload */}
        <label className="file-upload">
          <input type="file" accept="video/*" onChange={handleUpload} disabled={loading} />
          <div className={`upload-box ${video ? "uploaded" : ""}`}>
            {video ? `📹 ${video.name}` : "Choose a video"}
          </div>
        </label>

        {/* Language Selection */}
        <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: "12px", opacity: 0.8 }}>Source Language</label>
            <select 
              value={sourceLanguage} 
              onChange={(e) => setSourceLanguage(e.target.value)}
              disabled={loading}
              style={{ width: "100%" }}
            >
              {languages.map(lang => (
                <option key={lang.code} value={lang.code}>{lang.name}</option>
              ))}
            </select>
          </div>
          
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: "12px", opacity: 0.8 }}>Target Language</label>
            <select 
              value={targetLanguage} 
              onChange={(e) => setTargetLanguage(e.target.value)}
              disabled={loading}
              style={{ width: "100%" }}
            >
              {languages.map(lang => (
                <option key={lang.code} value={lang.code}>{lang.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Advanced Options */}
        <motion.div style={{ marginTop: "15px" }}>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            style={{
              background: "none",
              border: "1px solid rgba(255,255,255,0.2)",
              color: "white",
              padding: "8px 15px",
              borderRadius: "5px",
              cursor: "pointer",
              fontSize: "12px"
            }}
          >
            {showAdvanced ? "▼" : "▶"} Advanced Options
          </button>
          
          {showAdvanced && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              style={{
                marginTop: "10px",
                padding: "15px",
                background: "rgba(255,255,255,0.05)",
                borderRadius: "8px",
                fontSize: "13px"
              }}
            >
              <label style={{ display: "flex", alignItems: "center", marginBottom: "8px" }}>
                <input
                  type="checkbox"
                  checked={useWhisperX}
                  onChange={(e) => setUseWhisperX(e.target.checked)}
                  disabled={loading}
                  style={{ marginRight: "8px" }}
                />
                Use WhisperX (better timestamps)
              </label>
              
              <label style={{ display: "flex", alignItems: "center", marginBottom: "8px" }}>
                <input
                  type="checkbox"
                  checked={useDiarization}
                  onChange={(e) => setUseDiarization(e.target.checked)}
                  disabled={loading}
                  style={{ marginRight: "8px" }}
                />
                Speaker Diarization
              </label>
              
              <label style={{ display: "flex", alignItems: "center", marginBottom: "8px" }}>
                <input
                  type="checkbox"
                  checked={useEmotion}
                  onChange={(e) => setUseEmotion(e.target.checked)}
                  disabled={loading}
                  style={{ marginRight: "8px" }}
                />
                Emotion Detection
              </label>
              
              <label style={{ display: "flex", alignItems: "center", marginBottom: "8px" }}>
                <input
                  type="checkbox"
                  checked={useElevenLabs}
                  onChange={(e) => setUseElevenLabs(e.target.checked)}
                  disabled={loading}
                  style={{ marginRight: "8px" }}
                />
                ElevenLabs TTS (requires API key)
              </label>
              
              <label style={{ display: "flex", alignItems: "center" }}>
                <input
                  type="checkbox"
                  checked={useWav2Lip}
                  onChange={(e) => setUseWav2Lip(e.target.checked)}
                  disabled={loading}
                  style={{ marginRight: "8px" }}
                />
                Wav2Lip Lip-Sync (requires setup)
              </label>
            </motion.div>
          )}
        </motion.div>

        {/* Dub Button */}
        <motion.button
          className="dub-btn"
          whileTap={{ scale: 0.95 }}
          onClick={handleDub}
          disabled={loading}
          style={{ marginTop: "20px" }}
        >
          {loading ? "⏳ Processing..." : "🎙 Generate Dub"}
        </motion.button>

        {/* Progress */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ marginTop: "20px" }}
          >
            <VoiceWave loading={loading} />
            
            <div style={{ marginTop: "15px" }}>
              <div style={{
                width: "100%",
                height: "8px",
                background: "rgba(255,255,255,0.1)",
                borderRadius: "10px",
                overflow: "hidden"
              }}>
                <div style={{
                  width: `${progress}%`,
                  height: "100%",
                  background: "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
                  transition: "width 0.3s ease"
                }} />
              </div>
              
              <p style={{ marginTop: "10px", fontSize: "14px" }}>
                <strong>{progress}%</strong> - {getStageDescription(stage)}
              </p>
              <p style={{ fontSize: "12px", opacity: 0.7 }}>{message}</p>
            </div>
          </motion.div>
        )}

        {/* Result */}
        {dubbedVideo && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="video-preview"
            style={{ marginTop: "30px" }}
          >
            <h3>📽 Preview & Download</h3>
            <video src={dubbedVideo} controls width="100%" style={{ borderRadius: "10px" }} />
            
            <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
              <a 
                href={dubbedVideo} 
                download="dubbed_video.mp4"
                style={{
                  flex: 1,
                  padding: "12px",
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "white",
                  textDecoration: "none",
                  borderRadius: "8px",
                  textAlign: "center",
                  fontWeight: "bold"
                }}
              >
                ⬇️ Download Video
              </a>
              
              {transcript && (
                <button
                  onClick={downloadTranscript}
                  style={{
                    flex: 1,
                    padding: "12px",
                    background: "rgba(255,255,255,0.1)",
                    color: "white",
                    border: "1px solid rgba(255,255,255,0.3)",
                    borderRadius: "8px",
                    fontWeight: "bold",
                    cursor: "pointer"
                  }}
                >
                  📄 Download Transcript
                </button>
              )}
            </div>
          </motion.div>
        )}
      </motion.div>
      <Footer />
    </div>
  );
}

