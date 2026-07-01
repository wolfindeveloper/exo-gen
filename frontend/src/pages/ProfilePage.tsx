import { motion } from 'framer-motion';
import { HudBar } from '../components/HudBar';

export function ProfilePage() {
  return (
    <div className="flex flex-col h-screen bg-transparent">
      <div className="px-4 pt-4">
        <HudBar />
      </div>
      <div className="flex-1 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="glass-panel rounded-2xl p-8 w-full max-w-md"
        >
          <h1 className="text-2xl font-bold text-center neon-text-cyan">Профиль</h1>
          <p className="text-white/60 text-center mt-4 text-sm">
            Ваша статистика и достижения
          </p>
        </motion.div>
      </div>
    </div>
  );
}
