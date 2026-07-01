import { motion } from 'framer-motion';
import { useGameStore } from '../store/gameStore';

export function ProfilePage() {
  const player = useGameStore((s) => s.player);

  return (
    <div className="p-4 pb-28">
      <motion.header
        className="mb-5"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="font-display text-lg uppercase tracking-[0.2em] text-neon-purple">Профиль</h1>
        <p className="text-xs text-slate-500 mt-1">Ваша космическая карточка</p>
      </motion.header>

      <div className="glass-card p-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-neon-cyan to-neon-purple flex items-center justify-center text-2xl font-display text-white">
            {(player?.username || 'P')[0].toUpperCase()}
          </div>
          <div>
            <h2 className="text-lg font-display text-white">{player?.username || 'Капитан'}</h2>
            <p className="text-xs text-slate-500">ID: {player?.telegram_id}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-space-700/50 rounded-xl p-4 border border-white/5">
            <div className="text-[10px] text-slate-500 uppercase tracking-wider">XGen</div>
            <div className="text-xl font-bold text-neon-cyan mt-1">{player?.xgen_balance ?? 0}</div>
          </div>
          <div className="bg-space-700/50 rounded-xl p-4 border border-white/5">
            <div className="text-[10px] text-slate-500 uppercase tracking-wider">Фрагменты</div>
            <div className="text-xl font-bold text-neon-amber mt-1">{player?.fragments_balance ?? 0}</div>
          </div>
          <div className="bg-space-700/50 rounded-xl p-4 border border-white/5">
            <div className="text-[10px] text-slate-500 uppercase tracking-wider">XP</div>
            <div className="text-xl font-bold text-white mt-1">{player?.xp ?? 0}</div>
          </div>
          <div className="bg-space-700/50 rounded-xl p-4 border border-white/5">
            <div className="text-[10px] text-slate-500 uppercase tracking-wider">Серия</div>
            <div className="text-xl font-bold text-neon-green mt-1">{player?.daily_streak ?? 0} 🔥</div>
          </div>
        </div>
      </div>
    </div>
  );
}
