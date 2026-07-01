import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useGameStore } from './store/gameStore';
import { Loader2 } from 'lucide-react';
import { NavBar } from './components/layout/NavBar';
import { ShipPage } from './pages/ShipPage';
import { ZonesPage } from './pages/ZonesPage';
import { InventoryPage } from './pages/InventoryPage';
import { ProfilePage } from './pages/ProfilePage';

function AppContent() {
  const { player, isLoading, error, initApp } = useGameStore();

  useEffect(() => {
    initApp();
  }, [initApp]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-cosmos-900">
        <Loader2 className="w-12 h-12 text-accent-blue animate-spin" />
        <p className="mt-4 text-text-secondary text-lg">Загрузка галактики...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-cosmos-900 p-4">
        <p className="text-red-500 text-lg text-center">Ошибка: {error}</p>
      </div>
    );
  }

  if (!player) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-cosmos-900">
        <p className="text-text-secondary text-lg">Игрок не найден</p>
      </div>
    );
  }

  return (
    <>
      <Routes>
        <Route path="/" element={<ShipPage />} />
        <Route path="/zones" element={<ZonesPage />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
      <NavBar />
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
