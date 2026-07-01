import { HudBar } from '../components/HudBar';

export function ZonesPage() {
  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-cosmos-900 to-cosmos-800">
      <div className="px-4 pt-4">
        <HudBar />
      </div>
      <div className="flex-1 flex items-center justify-center">
        <h1 className="text-2xl font-bold text-text-primary">Зоны экспедиций</h1>
      </div>
    </div>
  );
}
