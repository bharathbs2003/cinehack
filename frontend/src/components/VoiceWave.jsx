import { motion } from "framer-motion";

export default function VoiceWave({ loading }) {
  const bars = Array.from({ length: 8 });
  return loading ? (
    <div className="voice-wave">
      {bars.map((_, i) => (
        <motion.div
          key={i}
          className="bar"
          animate={{ scaleY: [1, Math.random() * 2 + 1, 1] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.1 }}
        />
      ))}
    </div>
  ) : null;
}
