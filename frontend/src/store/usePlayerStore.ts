import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { PlayerRead, ShipConfig } from '../types'
import { get as apiGet } from '../lib/api'

/** Статус корабля */
export type ShipStatus = 'ready' | 'repair' | 'expedition' | 'staked'

/** Корабль игрока с дополнительными полями */
export interface PlayerShip extends ShipConfig {
  id: string
  stability: number
  status: ShipStatus
  inRepair: boolean
  repairUntil?: string
}

const MOCK_PLAYER: PlayerRead = {
  id: 'player_123',
  telegram_id: 123,
  username: 'Навигатор',
  level: 5,
  xp: 420,
  tier: 1,
  xgen_balance: 12450,
  verification_status: 'basic',
}

/** Моковые корабли для dev-режима */
const MOCK_SHIPS: PlayerShip[] = [
  {
    id: 'ship_1',
    slug: 'seeker_dust_runner',
    name: { ru: 'Искатель «Пыльный Бегун»', en: 'Seeker "Dust-Runner"', la: 'Seeker "Dust-Runner"' },
    short_description: { ru: 'Компактный разведчик', en: 'Compact scout', la: 'Explorator compactus' },
    description: { ru: '', en: '', la: '' },
    image_path: '/assets/ships/seeker_dust_runner.png',
    tier: 1,
    is_nft: false,
    base_stability: 100,
    expedition_slots: 1,
    stability: 100,
    status: 'ready',
    inRepair: false,
  },
  {
    id: 'ship_2',
    slug: 'vanguard_nebula_ghost',
    name: { ru: 'Авангард «Призрак Туманности»', en: 'Vanguard "Nebula Ghost"', la: 'Vanguard "Nebula Ghost"' },
    short_description: { ru: 'Быстрый ударный корабль', en: 'Fast strike ship', la: 'Navis ictus velox' },
    description: { ru: '', en: '', la: '' },
    image_path: '/assets/ships/vanguard_nebula_ghost.png',
    tier: 2,
    is_nft: false,
    base_stability: 100,
    expedition_slots: 2,
    stability: 100,
    status: 'ready',
    inRepair: false,
  },
]

interface PlayerState {
  player: PlayerRead | null
  ships: PlayerShip[]
  isLoading: boolean
  error: string | null
  repairMats: Record<string, number>
  language: 'ru' | 'en' | 'la'
  fetchPlayer: () => Promise<void>
  fetchShips: () => Promise<void>
  updateBalance: (delta: number) => void
  addResource: (slug: string, quantity: number) => void
  addEssence: (slug: string, quantity: number) => void
  addRepairMat: (slug: string, quantity: number) => void
  updateShipStatus: (shipSlug: string, status: ShipStatus) => void
  convertMats: (sourceTier: number, amount: number) => Promise<boolean>
  setLanguage: (lang: 'ru' | 'en' | 'la') => void
  getAvailableShips: () => PlayerShip[]
}

export const usePlayerStore = create<PlayerState>()(
  persist(
    (set, get) => ({
      player: null,
      ships: MOCK_SHIPS,
      isLoading: false,
      error: null,
      repairMats: {
        repair_matter_t1: 20,
        repair_matter_t2: 10,
        repair_matter_t3: 5,
        repair_matter_t4: 3,
        repair_matter_t5: 1,
      },
      language: 'ru',

      fetchPlayer: async () => {
        set({ isLoading: true, error: null })
        try {
          const player = await apiGet('/player/me') as PlayerRead
          set({ player, isLoading: false })
        } catch (err) {
          console.warn('API fetch failed, using mock data:', err)
          set({ player: MOCK_PLAYER, isLoading: false, error: null })
        }
      },

      fetchShips: async () => {
        try {
          const ships = await apiGet('/ships') as PlayerShip[]
          set({ ships })
        } catch {
          // Используем моковые корабли
          set({ ships: MOCK_SHIPS })
        }
      },

      updateBalance: (delta: number) =>
        set((state) => {
          if (!state.player) return state
          return {
            player: {
              ...state.player,
              xgen_balance: Math.max(0, state.player.xgen_balance + delta),
            },
          }
        }),

      addResource: (_slug: string, _quantity: number) => {
        // Inventory management placeholder
      },

      addEssence: (_slug: string, _quantity: number) => {
        // Essence management placeholder
      },

      addRepairMat: (slug: string, quantity: number) =>
        set((state) => ({
          repairMats: {
            ...state.repairMats,
            [slug]: (state.repairMats[slug] || 0) + quantity,
          },
        })),

      convertMats: async (sourceTier: number, amount: number) => {
        try {
          const { post } = await import('../lib/api')
          const result = await post('/resources/convert', {
            source_tier: sourceTier,
            amount,
          })
          set((state) => {
            const sourceSlug = `repair_matter_t${sourceTier}`
            const targetSlug = `repair_matter_t${sourceTier - 1}`
            return {
              repairMats: {
                ...state.repairMats,
                [sourceSlug]: (state.repairMats[sourceSlug] || 0) - amount,
                [targetSlug]: (state.repairMats[targetSlug] || 0) + (result as any).target_amount,
              },
            }
          })
          return true
        } catch (err) {
          console.error('Convert mats failed:', err)
          return false
        }
      },

      updateShipStatus: (shipSlug: string, status: ShipStatus) =>
        set((state) => ({
          ships: state.ships.map((ship) =>
            ship.slug === shipSlug
              ? {
                  ...ship,
                  status,
                  inRepair: status === 'repair',
                }
              : ship
          ),
        })),

      setLanguage: (lang: 'ru' | 'en' | 'la') => set({ language: lang }),

      getAvailableShips: () => {
        const { ships } = get()
        return ships.filter((s) => s.status === 'ready' && !s.inRepair)
      },
    }),
    {
      name: 'exo-player-storage',
      partialize: (state) => ({ player: state.player, ships: state.ships, repairMats: state.repairMats, language: state.language }),
    }
  )
)
