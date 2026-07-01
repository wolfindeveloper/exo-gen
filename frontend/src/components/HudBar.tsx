import { Coins, Puzzle, Star } from 'lucide-react';
import { useGameStore } from '../store/gameStore';

export function HudBar() {
  const player = useGameStore((state) => state.player);

  if (!player) return null;

  const avatarLetter = (player.username || 'P')[0].toUpperCase();

  return (
    <div className="flex items-center gap-3 px-4 py-3 bg-cosmos-800 rounded-lg">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-accent-purple flex items-center justify-center text-sm font-bold">
          {avatarLetter}
        </div>
        <span className="text-sm text-text-primary font-medium truncate max-w-20">
          {player.username || 'Player'}
        </span>
      </div>

      <div className="flex items-center gap-1 text-sm">
        <Coins className="w-4 h-4 text-yellow-400" />
        <span className="text-text-primary">{player.xgen_balance}</span>
      </div>

      <div className="flex items-center gap-1 text-sm">
        <Puzzle className="w-4 h-4 text-accent-green" />
        <span className="text-text-primary">{player.fragments_balance}</span>
      </div>

      <div className="flex items-center gap-1 text-sm">
        <Star className="w-4 h-4 text-accent-blue" />
        <span className="text-text-primary">{player.xp}</span>
      </div>
    </div>
  );
}
