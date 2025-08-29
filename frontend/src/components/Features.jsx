import { motion } from "framer-motion";

export default function Features() {
  return (
    <section className="features">
      <h2>✨ Features</h2>
      <div className="feature-cards">
        <motion.div className="card" whileHover={{ scale: 1.1 }}>🌍 20+ Languages</motion.div>
        <motion.div className="card" whileHover={{ scale: 1.1 }}>🎙 Human-like Voices</motion.div>
        <motion.div className="card" whileHover={{ scale: 1.1 }}>⚡ Fast AI Processing</motion.div>
      </div>
    </section>
  );
}
