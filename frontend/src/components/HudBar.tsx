import { Coins, Puzzle, Star } from 'lucide-react';
import { useGameStore } from '../store/gameStore';

export function HudBar() {
  const player = useGameStore((state) => state.player);

  if (!player) return null;

  const avatarLetter = (player.username || 'P')[0].toUpperCase();

  return (
    <div className="glass-panel rounded-b-2xl px-4 py-3">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-full neon-border-cyan flex items-center justify-center">
            <span className="text-sm font-bold text-white">{avatarLetter}</span>
          </div>
          <span className="text-sm text-white font-medium truncate max-w-20">
            {player.username || 'Player'}
          </span>
        </div>

        <div className="flex-1" />

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <Coins className="w-4 h-4 text-amber-400 drop-shadow-[0_0_4px_rgba(251,191,36,0.6)]" />
            <span className="text-sm font-bold text-white">{player.xgen_balance}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <Puzzle className="w-4 h-4 text-purple-400 drop-shadow-[0_0_4px_rgba(192,132,252,0.6)]" />
            <span className="text-sm font-bold text-white">{player.fragments_balance}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <Star className="w-4 h-4 text-cyan-400 drop-shadow-[0_0_4px_rgba(34,211,238,0.6)]" />
            <span className="text-sm font-bold text-white">{player.xp}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
