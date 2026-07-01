import { useNavigate } from 'react-router-dom';
import { Rocket } from 'lucide-react';
import { HudBar } from '../components/HudBar';

const TEA_LEVEL = 80;
const OPTIMISM = 45;

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

  const handleSlotClick = () => {
    alert('Слот артефакта');
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-cosmos-900 to-cosmos-800">
      <div className="px-4 pt-4">
        <HudBar />
      </div>

      <div className="px-4 mt-4 space-y-2">
        <div>
          <div className="flex justify-between text-xs text-text-secondary mb-1">
            <span>Космическая заварка</span>
            <span>{TEA_LEVEL}%</span>
          </div>
          <div className="h-2 bg-cosmos-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all"
              style={{ width: `${TEA_LEVEL}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs text-text-secondary mb-1">
            <span>Уровень оптимизма</span>
            <span>{OPTIMISM}%</span>
          </div>
          <div className="h-2 bg-cosmos-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-accent-blue rounded-full transition-all"
              style={{ width: `${OPTIMISM}%` }}
            />
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center relative px-4">
        <div className="relative w-64 h-64">
          <div className="absolute inset-0 flex items-center justify-center">
            <Rocket className="w-48 h-48 text-text-secondary" strokeWidth={1} />
          </div>

          {slotPositions.map((pos, index) => (
            <button
              key={index}
              onClick={handleSlotClick}
              className="absolute w-10 h-10 rounded-full border-2 border-dashed border-text-secondary/50 hover:border-accent-blue transition-colors"
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
          className="w-full py-4 bg-accent-purple hover:bg-accent-purple/90 text-white font-semibold rounded-xl transition-colors"
        >
          Отправиться в экспедицию
        </button>
      </div>
    </div>
  );
}
