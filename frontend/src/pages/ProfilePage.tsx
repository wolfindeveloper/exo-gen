import { HudBar } from '../components/HudBar';

export function ProfilePage() {
  return (
    <div className="flex flex-col h-screen bg-[#0A0B0E]">
      <div className="px-4 pt-4">
        <HudBar />
      </div>
      <div className="flex-1 flex items-center justify-center">
        <h1 className="text-2xl font-bold text-white/70">Профиль</h1>
      </div>
    </div>
  );
}
