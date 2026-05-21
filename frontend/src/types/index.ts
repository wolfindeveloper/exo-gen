export interface PlayerRead {
  id: string
  telegram_id: number
  username: string
  level: number
  xp: number
  tier: number
  xgen_balance: number
  verification_status: 'none' | 'basic' | 'verified'
}

export interface PlayerUpdate {
  username?: string
  language?: 'ru' | 'en' | 'la'
  avatar_slug?: string
  notifications_enabled?: boolean
}

export interface ShipConfig {
  name: Record<string, string>
  short_description: Record<string, string>
  description: Record<string, string>
  image_path: string
  art_path?: string
  tier: number
  slug: string
  is_nft: boolean
  base_stability: number
  expedition_slots: number
}

export interface ExpeditionConfig {
  name: Record<string, string>
  description: Record<string, string>
  slug: string
  tier: number
  duration_hours: number
  xp_reward: number
  fuel_required: string[]
  loot_table: string[]
  damage_chance_percent: number
  requires_verification?: string
}

export interface GalaxyZoneConfig {
  name: Record<string, string>
  description: Record<string, string>
  image_path: string
  slug: string
  tier: number
  lore: string | Record<string, string>
  drop_table: string[]
  risk_pct?: number
  rare_chance?: number
  loot_table?: Array<{ essence_slug: string; weight: number }>
  repair_drop_weights?: Record<string, number>
}

export interface ArtifactRead {
  id: string
  slug: string
  recipe_hash: string
  status: string
  cycles_remaining: number
  staked_at: string | null
  accumulated_yield: number
  bonus_multiplier: number
  domain_slug: string
  created_at: string
}

export interface ExpeditionRead {
  id: string
  ship_id: string
  slug: string
  tier: number
  overdrive_mode: string
  status: string
  started_at: string
  estimated_end: string
  completed_at: string | null
  loot: Record<string, number> | null
  xp_reward: number
  damage_occurred: boolean
}

export interface WalletConnectResponse {
  address: string
  network: string
  ton_balance: number
  xgen_balance: number
  connected: boolean
}

export interface CraftRequest {
  domain_slug: string
  essences: string[]
  xgen_amount: number
}

export interface CraftResponse {
  status: 'created' | 'taken'
  recipe_hash: string
  artifact_id: string | null
  essences_refunded: string[] | null
  xgen_burned: number
}

export type Rarity = 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary'

export const TIER_TO_RARITY: Record<number, Rarity> = {
  1: 'common',
  2: 'uncommon',
  3: 'rare',
  4: 'epic',
  5: 'legendary',
}

export interface BaseResource {
  slug: string
  name: { ru: string; en: string; la?: string }
  short_description: { ru: string; en: string; la?: string }
  description: { ru: string; en: string; la?: string }
  icon_path?: string
  art_path?: string
  lore: { ru: string; en: string; la?: string }
  tier: number
  rarity: Rarity
  type: 'fuel' | 'essence' | 'artifact'
}

export interface Fuel extends BaseResource {
  type: 'fuel'
  image_path: string
  stats: { efficiency: number; burn_rate: number }
}

export interface Essence extends BaseResource {
  type: 'essence'
  domain: string
  crafting_weight: number
}

export interface Artifact extends BaseResource {
  type: 'artifact'
  bonus: { type: string; value: number; display: { ru: string; en: string; la?: string } }
  crafting_recipe: string[]
  is_discovered: boolean
  discovered_by: string[]
  discovered_at: string | null
}

export type ResourceItem = Fuel | Essence | Artifact | RepairMat

export interface RepairMat {
  slug: string
  name: { ru: string; en: string; la?: string }
  short_description: { ru: string; en: string; la?: string }
  description: { ru: string; en: string; la?: string }
  icon_path: string
  tier: number
  repair_value: number
  rarity?: Rarity
  type: 'repair_mat'
  lore: { ru: string; en: string; la?: string }
}

export interface Ship {
  id: string
  player_id: string
  slug: string
  stability: number
  is_nft: boolean
  is_staked: boolean
  in_repair: boolean
  repair_mode: string | null
  repair_until: string | null
  expedition_cycles: number
  created_at: string
}

export interface RepairInfo {
  ship_id: string
  stability: number
  ship_tier: number
  mat_slug: string
  mat_name: string
  repair_value: number
  required_mats: number
  owned_mats: number
  can_repair: boolean
}
