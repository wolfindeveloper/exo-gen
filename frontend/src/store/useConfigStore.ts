import { create } from 'zustand'
import { get } from '../lib/api'
import type { ShipConfig, GalaxyZoneConfig, ExpeditionConfig, Fuel, Essence, Artifact, RepairMat } from '../types'

interface ConfigState {
  ships: Record<string, ShipConfig>
  zones: Record<string, GalaxyZoneConfig>
  expeditions: Record<string, ExpeditionConfig>
  avatars: Record<string, { name: Record<string, string>; slug: string; image_path: string }>
  fuels: Record<string, Fuel>
  essences: Record<string, Essence>
  artifacts: Record<string, Artifact>
  repairMats: Record<string, RepairMat>
  isLoading: boolean
  loadConfigs: () => Promise<void>
}

export const useConfigStore = create<ConfigState>()((set) => ({
  ships: {},
  zones: {},
  expeditions: {},
  avatars: {},
  fuels: {},
  essences: {},
  artifacts: {},
  repairMats: {},
  isLoading: false,

  loadConfigs: async () => {
    set({ isLoading: true })
    try {
      const [shipsRaw, zonesRaw, expeditionsRaw, avatarsRaw, fuelsRaw, essencesRaw, artifactsRaw, repairMatsRaw] = await Promise.all([
        get<Record<string, ShipConfig>>('/config/ships'),
        get<Record<string, GalaxyZoneConfig>>('/config/galaxy_zones'),
        get<Record<string, ExpeditionConfig>>('/config/expeditions'),
        get<Record<string, { name: Record<string, string>; slug: string; image_path: string }>>('/config/avatars'),
        get<Record<string, Fuel>>('/config/fuels'),
        get<Record<string, Essence>>('/config/essences'),
        get<Record<string, Artifact>>('/config/artifacts'),
        get<Record<string, RepairMat>>('/config/repair_mats'),
      ])

      const zonesRawAny = zonesRaw as Record<string, unknown>
      const zones = zonesRawAny.galaxy_zones
        ? zonesRawAny.galaxy_zones as Record<string, GalaxyZoneConfig>
        : zonesRaw as Record<string, GalaxyZoneConfig>

      set({
        ships: shipsRaw,
        zones,
        expeditions: expeditionsRaw,
        avatars: avatarsRaw,
        fuels: fuelsRaw,
        essences: essencesRaw,
        artifacts: artifactsRaw,
        repairMats: repairMatsRaw,
        isLoading: false,
      })
    } catch (err) {
      console.error('Failed to load configs:', err)
      set({ isLoading: false })
    }
  },
}))
