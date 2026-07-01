import { useNavigate } from 'react-router-dom';
import { Rocket } from 'lucide-react';
import { HudBar } from '../components/HudBar';
import { useGameStore } from '../store/gameStore';

const slotPositions = [
  { top: '5%', left: '50%' },
  { top: '20%', left: '85%' },
  { top: '50%', left: '95%' },
  { top: '80%', left: '85%' },
  { top: '95%', left: '50%' },
  { top: '80%', left: '15%' },
  { top: '50%', left: '5%' },
  { top: '20%', left: '15%' },
];

export function ShipPage() {
  const navigate = useNavigate();
  const ship = useGameStore((state) => state.ship);

  const teaLevel = ship?.tea_level ?? 80;
  const optimism = ship?.optimism ?? 45;

  const handleSlotClick = () => {
    alert('Слот артефакта');
  };

  return (
    <div className="flex flex-col h-screen bg-transparent">
      <div className="px-4 pt-4">
        <HudBar />
      </div>

      <div className="px-4 mt-4">
        <div className="glass-panel rounded-xl p-4 space-y-3">
          <div>
            <div className="flex justify-between text-xs text-white/60 mb-2">
              <span className="font-medium">Космическая заварка</span>
              <span className="font-bold text-green-400">{Math.round(teaLevel)}%</span>
            </div>
            <div className="h-[10px] bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all duration-500 shadow-[0_0_12px_rgba(34,197,94,0.6)]"
                style={{ width: `${teaLevel}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs text-white/60 mb-2">
              <span className="font-medium">Уровень оптимизма</span>
              <span className="font-bold text-cyan-400">{Math.round(optimism)}%</span>
            </div>
            <div className="h-[10px] bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-blue-400 rounded-full transition-all duration-500 shadow-[0_0_12px_rgba(6,182,212,0.6)]"
                style={{ width: `${optimism}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 relative flex items-center justify-center px-4">
        <div className="relative w-72 h-72">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-float">
              <div className="relative">
                <Rocket 
                  className="w-40 h-40 text-gray-200 drop-shadow-[0_0_30px_rgba(255,255,255,0.3)]" 
                  strokeWidth={1.2} 
                />
              </div>
            </div>
          </div>

          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-32 h-4 bg-black/40 rounded-full blur-xl" />

          {slotPositions.map((pos, index) => (
            <button
              key={index}
              onClick={handleSlotClick}
              className="absolute w-14 h-14 hexagon bg-black/60 border border-white/10 flex items-center justify-center hover:neon-border-cyan transition-all duration-300 group"
              style={{
                top: pos.top,
                left: pos.left,
                transform: 'translate(-50%, -50%)',
              }}
            >
              <div className="w-10 h-10 hexagon bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center">
                <div className="w-2 h-2 rounded-full bg-white/20 group-hover:bg-cyan-400 group-hover:shadow-[0_0_8px_rgba(26,218,252,0.8)] transition-all" />
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="px-4 pb-24">
        <div className="glass-panel rounded-xl p-1">
          <button
            onClick={() => navigate('/zones')}
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold py-4 rounded-xl shadow-lg shadow-cyan-500/30 transition-all active:scale-95 hover:shadow-cyan-500/50"
          >
            Отправиться в экспедицию
          </button>
        </div>
      </div>
    </div>
  );
}
