import { useCallback } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../store/gameStore';

export function HudBar() {
  const navigate = useNavigate();
  const player = useGameStore((s) => s.player);

  const handleAvatarClick = useCallback(() => {
    navigate('/profile');
  }, [navigate]);

  if (!player) return null;

  const avatarLetter = (player.username || 'P')[0].toUpperCase();

  return (
    <motion.header
      className="flex items-center gap-2 px-4 py-2.5 border-b border-white/5"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <button
        onClick={handleAvatarClick}
        className="w-9 h-9 rounded-full bg-gradient-to-br from-neon-cyan to-neon-purple shrink-0 overflow-hidden transition-transform active:scale-95"
      >
        <div className="w-full h-full flex items-center justify-center text-[10px] font-display text-white">
          {avatarLetter}
        </div>
      </button>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 min-w-0">
          <span className="text-sm font-display truncate text-slate-200">
            {player.username || 'Капитан'}
          </span>
        </div>
      </div>

      <span className="text-[11px] text-neon-cyan font-mono tabular-nums shrink-0">
        🔷{player.xgen_balance}
      </span>
      <span className="text-[11px] text-amber-400/80 font-mono tabular-nums shrink-0">
        📜{player.fragments_balance}
      </span>
    </motion.header>
  );
}
