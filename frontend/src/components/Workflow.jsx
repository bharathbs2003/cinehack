import { motion } from "framer-motion";

export default function Workflow() {
  return (
    <section className="workflow">
      <h2>🔄 Workflow</h2>
      <div className="steps">
        <motion.div className="step" whileHover={{ scale: 1.05 }}>1. Upload</motion.div>
        <motion.div className="step" whileHover={{ scale: 1.05 }}>2. Select Language</motion.div>
        <motion.div className="step" whileHover={{ scale: 1.05 }}>3. AI Dub</motion.div>
        <motion.div className="step" whileHover={{ scale: 1.05 }}>4. Download</motion.div>
      </div>
    </section>
  );
}
