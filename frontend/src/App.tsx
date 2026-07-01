import { useEffect } from 'react';
import { useGameStore } from './store/gameStore';
import { Loader2 } from 'lucide-react';

function App() {
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
    <div className="min-h-screen bg-cosmos-900 p-4">
      <div className="max-w-md mx-auto pt-8">
        <h1 className="text-2xl font-bold text-text-primary mb-4">
          Добро пожаловать, {player.username || 'Путешественник'}!
        </h1>
        <div className="bg-cosmos-800 rounded-lg p-4">
          <p className="text-text-secondary">
            Ваш XGen: <span className="text-accent-blue font-semibold">{player.xgen_balance}</span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
