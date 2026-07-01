import { create } from 'zustand';
import type { Player, Ship } from '../types';
import { registerPlayer, getMe } from '../api/routes';
import { getTelegramUser } from '../lib/telegram';

interface GameState {
  player: Player | null;
  ship: Ship | null;
  isLoading: boolean;
  error: string | null;
  initApp: () => Promise<void>;
  setPlayer: (player: Player) => void;
  setShip: (ship: Ship) => void;
  setError: (error: string | null) => void;
}

export const useGameStore = create<GameState>((set) => ({
  player: null,
  ship: null,
  isLoading: true,
  error: null,

  initApp: async () => {
    try {
      set({ isLoading: true, error: null });

      const telegramUser = getTelegramUser();
      
      if (!telegramUser) {
        throw new Error('Telegram user not found');
      }

      const telegramId = telegramUser.id;
      const username = telegramUser.username || telegramUser.first_name;

      await registerPlayer(telegramId, username);

      const player = await getMe();
      set({ player, isLoading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to initialize app';
      set({ error: errorMessage, isLoading: false });
    }
  },

  setPlayer: (player) => set({ player }),
  setShip: (ship) => set({ ship }),
  setError: (error) => set({ error }),
}));
