import { useNavigate } from 'react-router-dom';
import { Rocket } from 'lucide-react';
import { HudBar } from '../components/HudBar';
import { useGameStore } from '../store/gameStore';

const slotPositions = [
  { top: '0%', left: '50%' },
  { top: '15%', left: '85%' },
  { top: '50%', left: '100%' },
  { top: '85%', left: '85%' },
  { top: '100%', left: '50%' },
  { top: '85%', left: '15%' },
  { top: '50%', left: '0%' },
  { top: '15%', left: '15%' },
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
    <div className="flex flex-col h-screen bg-[#0A0B0E]">
      <div className="px-4 pt-4">
        <HudBar />
      </div>

      <div className="px-4 mt-4">
        <div className="bg-white/5 p-4 rounded-2xl backdrop-blur-sm space-y-3">
          <div>
            <div className="flex justify-between text-xs text-white/60 mb-1">
              <span>Космическая заварка</span>
              <span>{Math.round(teaLevel)}%</span>
            </div>
            <div className="h-2.5 bg-white/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-[#22c55e] rounded-full transition-all duration-500 shadow-[0_0_12px_#22c55e80]"
                style={{ width: `${teaLevel}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs text-white/60 mb-1">
              <span>Уровень оптимизма</span>
              <span>{Math.round(optimism)}%</span>
            </div>
            <div className="h-2.5 bg-white/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-[#1ADAFC] rounded-full transition-all duration-500 shadow-[0_0_12px_#1ADAFC80]"
                style={{ width: `${optimism}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center relative px-4">
        <div className="relative w-64 h-64">
          <div className="absolute inset-8 rounded-full border border-cyan-500/30 bg-cyan-500/5 shadow-[0_0_60px_rgba(26,218,252,0.15)] flex items-center justify-center">
            <Rocket className="w-40 h-40 text-gray-300 drop-shadow-[0_0_20px_rgba(255,255,255,0.2)]" strokeWidth={1} />
          </div>

          {slotPositions.map((pos, index) => (
            <button
              key={index}
              onClick={handleSlotClick}
              className="absolute w-12 h-12 rounded-full bg-black/50 border border-dashed border-white/20 hover:border-[#1ADAFC] hover:shadow-[0_0_12px_#1ADAFC40] transition-all duration-200"
              style={{
                top: pos.top,
                left: pos.left,
                transform: 'translate(-50%, -50%)',
              }}
            />
          ))}
        </div>
      </div>

      <div className="px-4 pb-24">
        <button
          onClick={() => navigate('/zones')}
          className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-cyan-500/30 active:scale-95 transition-transform"
        >
          Отправиться в экспедицию
        </button>
      </div>
    </div>
  );
}
