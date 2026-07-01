import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useGameStore } from './store/gameStore';
import { NavBar } from './components/layout/NavBar';
import { HudBar } from './components/HudBar';
import ShipPage from './pages/ShipPage';
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
      <div className="min-h-screen text-white max-w-lg mx-auto relative z-10">
        <div className="flex flex-col items-center justify-center h-screen gap-4 px-6">
          <motion.div
            className="text-5xl"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          >
            🚀
          </motion.div>
          <p className="text-slate-500 text-xs font-display uppercase tracking-widest">
            Загрузка галактики...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen text-white max-w-lg mx-auto relative z-10">
        <div className="flex flex-col items-center justify-center h-screen gap-4 px-6">
          <motion.div
            className="text-5xl"
            animate={{ opacity: 0.3 }}
          >
            🌑
          </motion.div>
          <p className="text-slate-400 text-xs font-display uppercase tracking-widest text-center">
            Не удалось подключиться к серверу
          </p>
          <p className="text-slate-600 text-[10px] text-center max-w-xs">
            {error}
          </p>
          <button
            onClick={() => useGameStore.getState().initApp()}
            className="mt-4 px-6 py-2.5 rounded-xl bg-neon-cyan/10 text-neon-cyan text-xs font-display uppercase tracking-wider border border-neon-cyan/20 active:bg-neon-cyan/20 transition-colors"
          >
            Повторить
          </button>
        </div>
      </div>
    );
  }

  if (!player) {
    return (
      <div className="min-h-screen text-white max-w-lg mx-auto relative z-10">
        <div className="flex flex-col items-center justify-center h-screen">
          <p className="text-slate-500 text-xs">Игрок не найден</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen text-white max-w-lg mx-auto relative z-10 pb-16">
      <HudBar />
      <Routes>
        <Route path="/" element={<ShipPage />} />
        <Route path="/zones" element={<ZonesPage />} />
        <Route path="/inventory" element={<InventoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
      {error && (
        <div className="fixed top-0 left-0 right-0 z-[200] bg-red-900/90 backdrop-blur-xl p-3 text-center text-xs text-red-200 font-mono">
          Error: {error}
        </div>
      )}
      <NavBar />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="starfield" />
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
