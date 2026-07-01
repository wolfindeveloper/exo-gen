import { Coins, Puzzle, Star } from 'lucide-react';
import { useGameStore } from '../store/gameStore';

export function HudBar() {
  const player = useGameStore((state) => state.player);

  if (!player) return null;

  const avatarLetter = (player.username || 'P')[0].toUpperCase();

  return (
    <div className="flex items-center gap-3 px-4 py-3 bg-black/30 backdrop-blur-md border-b border-white/5 rounded-b-2xl">
      <div className="flex items-center gap-2">
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#8B5CF6] to-[#1ADAFC] p-[2px]">
          <div className="w-full h-full rounded-full bg-[#0A0B0E] flex items-center justify-center text-sm font-bold text-white">
            {avatarLetter}
          </div>
        </div>
        <span className="text-sm text-white font-medium truncate max-w-20">
          {player.username || 'Player'}
        </span>
      </div>

      <div className="flex-1" />

      <div className="flex items-center gap-1">
        <Coins className="w-4 h-4 text-[#f59e0b]" />
        <span className="text-sm font-bold text-white">{player.xgen_balance}</span>
      </div>

      <div className="flex items-center gap-1">
        <Puzzle className="w-4 h-4 text-[#a855f7]" />
        <span className="text-sm font-bold text-white">{player.fragments_balance}</span>
      </div>

      <div className="flex items-center gap-1">
        <Star className="w-4 h-4 text-[#1ADAFC]" />
        <span className="text-sm font-bold text-white">{player.xp}</span>
      </div>
    </div>
  );
}
