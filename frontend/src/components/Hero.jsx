import { motion } from "framer-motion";
import { Link } from "react-router-dom";

export default function Hero() {
  return (
    <motion.section
      className="hero-section"
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <h1 className="hero-title">🌍 EduDub AI</h1>
      <p className="hero-subtitle">
        Instantly dub your videos into 20+ languages with AI-powered human-like voices.
      </p>
      <Link to="/upload" className="cta-btn">🚀 Get Started</Link>
    </motion.section>
  );
}
