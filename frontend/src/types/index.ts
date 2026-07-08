export interface EffectiveStats {
  max_stability: number
  max_fuel: number
  speed_mod: number
  damage_reduction: number
  total_speed_bonus: number
  total_fuel_efficiency: number
}

export interface Ship {
  id: string
  name: string
  tea_level: number
  optimism: number
  speed: number
  defense: number
  luck: number
  equipment?: { artifacts: Array<{ id: string; name_key?: string; tier: number; icon_path?: string }> }
}

export interface Zone {
  id: string
  name: string
  description: string
  image_url: string
  fuel_cost: number
  optimism_risk: number
  duration_seconds: number
  loot_table: LootEntry[]
}

export interface LootEntry {
  item_id: string | null
  item_type: string
  amount: number
  chance: number
  item_name?: string | null
}

export interface UserProfile {
  id: string
  telegram_id: number
  username: string | null
  xp: number
  xgen_balance: number
  fragments_balance: number
  daily_streak: number
  ship_count: number
  ship_id: string
  level?: number
  balance_stars?: number
  daily_reward?: boolean
  streak_broken?: boolean
  daily_reward_items?: Record<string, number>
}

export interface ProfileStats {
  xp: number
  level: number
  total_expeditions: number
  total_artifacts_found: number
  unlocked_articles: number
}

export interface ItemReference {
  id: string
  name: string
  description: string
  type: string
  rarity: string
  effect: Record<string, unknown>
  is_tradable: boolean
  sell_price: number
}

export interface InventoryItem {
  item: ItemReference
  quantity: number
}

export interface Expedition {
  id: string
  ship_id: string
  zone_id: string
  started_at: string
  ends_at: string
  status: string
  remaining_tea: number
}

export interface ClaimResult {
  xgen_earned: number
  fragments_earned: number
  items_earned: ClaimedItem[]
  optimism_lost: number
  current_tea: number
  current_optimism: number
}

export interface ClaimedItem {
  item_id: string
  amount: number
}

export interface LootItem {
  item_config_id: string
  quantity: number
  name?: string | null
}

export interface LootResult {
  shipName: string
  loot: LootItem[]
  shipStability: number
  xpGained?: number
  level?: number
  leveledUp?: boolean
}

export interface Artifact {
  id: string
  name_key: string
  description_key?: string
  tier: number
  rarity: string
  stats_modifiers?: Record<string, number>
  icon_path?: string
}

export interface Resource {
  id: string
  name_key: string
  description_key?: string
  tier: number
  resource_type: string
  icon_path: string
}

export interface Rank {
  level: number
  title_key: string
  description_key: string
  icon_path: string
}

export interface ShipConfig {
  id: string
  name_key: string
  description_key: string
  tier: number
  stats: { stability: number; fuel_capacity: number; speed_mod: number }
  required_level: number
  art_path: string
}

export interface UserStats {
  total_expeditions: number
  completed_expeditions: number
  failed_expeditions: number
  artifacts_crafted: number
  joined_days: number
  total_xp_earned: number
  zones_explored: number
  equipped_artifacts_count: number
  unique_artifacts: number
  resources: { fuel: number; repair_kits: number }
  guide_progress: { total_chapters: number; completed_chapters: number; entries_researched: number }
  recent_expeditions: {
    id: string
    zone_config_id: string
    status: string
    end_time: string | null
    loot_summary: string | null
  }[]
  glitches_fixed: number
  total_purchases: number
}

export interface AchievementStatus {
  achievement_id: string
  claimed: boolean
  claimed_at: string | null
}

export interface ClaimAchievementResponse {
  status: string
  achievement_id: string
  xp_gained: number
  xgen_gained: number
}

export interface ShipActionResponse {
  ship: Ship
  inventory: InventoryItem[]
}

export interface GuideChapterSummary {
  id: string
  title: string
  description: string
  order: number
  is_secret: boolean
  reward_artifact_id: string
  total_entries: number
  researched_count: number
  all_researched: boolean
  reward_claimed: boolean
  entries: GuideEntrySummary[]
}

export interface GuideEntrySummary {
  id: string
  title: string
  fragment_cost: number
  status: 'locked' | 'researched' | 'glitched' | 'hidden'
  has_event?: boolean | null
  unlock_event?: string | null
}

export interface GuideEntryDetail extends GuideEntrySummary {
  text?: string | null
  glitch_chance?: number
}

export interface GuideChapterDetail {
  id: string
  title: string
  description: string
  is_secret: boolean
  reward_artifact_id: string
  total_entries: number
  researched_count: number
  all_researched: boolean
  reward_claimed: boolean
  entries: GuideEntryDetail[]
}

export interface GuideChaptersResponse {
  chapters: GuideChapterSummary[]
}

export interface GuideResearchResponse {
  status: string
  fixed: boolean
  balance_fragments: number
}

export interface GuideFixGlitchResponse {
  status: string
  balance_fragments: number
}

export interface GuideClaimRewardResponse {
  status: string
  artifact_id: string
  artifact_name: string
}

export interface ShopItem {
  id: string
  category: string
  name_key: string
  description_key: string
  price: { amount: number; currency: 'xgen' | 'stars' }
  rewards: { type: string; quantity?: number; tier?: number; item_type?: string; item_config_id?: string }[]
  icon_path?: string
  tier?: number
  rarity?: string
  stats_modifiers?: Record<string, number>
  type?: string
}

export interface ShopGrantedItem {
  type: string
  item_config_id?: string
  quantity?: number
  tier?: number
  name_key?: string
}

export interface ShopBuyResponse {
  status: string
  granted: ShopGrantedItem[]
  balance_xgen: number
  balance_stars: number
}

export type ItemType = 'consumable' | 'artifact' | 'material' | 'key_item' | 'loot_box'
export type ItemRarity = 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary'

export interface ConsumableEffect {
  restore_tea?: number | null
  restore_optimism?: number | null
}

export interface ArtifactEffect {
  bonus_speed?: number | null
  bonus_defense?: number | null
  bonus_capacity?: number | null
  bonus_luck?: number | null
  bonus_fuel?: number | null
  bonus_repair?: number | null
  bonus_xp?: number | null
  bonus_fragment?: number | null
}

export type ItemEffect = ConsumableEffect | ArtifactEffect

export interface AdminItem {
  id: string
  name: string
  description: string
  type: ItemType
  rarity: ItemRarity
  effect: Record<string, unknown>
  is_tradable: boolean
  sell_price: number
  image_url: string
}

export interface AdminItemsResponse {
  items: AdminItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface CreateItemPayload {
  name: string
  description: string
  type: ItemType
  rarity?: ItemRarity
  effect?: ItemEffect
  is_tradable?: boolean
  sell_price?: number
  image_url?: string
}

export interface UpdateItemPayload {
  name?: string
  description?: string
  rarity?: ItemRarity
  effect?: ItemEffect
  is_tradable?: boolean
  sell_price?: number
  image_url?: string
}

export type DropType = 'xgen' | 'fragments' | 'item'

export interface AdminLootItem {
  drop_type: DropType
  amount: number
  chance: number
  item_id: string | null
}

export interface AdminZone {
  id: string
  name: string
  description: string
  image_url: string
  fuel_cost: number
  optimism_risk: number
  duration_seconds: number
  loot_table: AdminLootItem[]
}

export interface AdminZonesResponse {
  items: AdminZone[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface LootDropPayload {
  drop_type: DropType
  amount: number
  chance: number
  item_id?: string | null
}

export interface CreateZonePayload {
  name: string
  description: string
  image_url: string
  fuel_cost: number
  optimism_risk: number
  duration_seconds: number
  loot_table: LootDropPayload[]
}

export interface UpdateZonePayload {
  name?: string
  description?: string
  image_url?: string
  fuel_cost?: number
  optimism_risk?: number
  duration_seconds?: number
  loot_table?: LootDropPayload[]
}

export interface AdminLootBoxEntry {
  item_type: string
  amount: number
  chance: number
  item_id: string | null
}

export interface AdminLootBox {
  id: string
  box_type: string
  name: string
  description: string
  entries: AdminLootBoxEntry[]
  is_active: boolean
}

export interface CreateLootBoxPayload {
  box_type: string
  name: string
  description: string
  entries: { item_type: string; amount: number; chance: number; item_id?: string | null }[]
  is_active?: boolean
}

export interface UpdateLootBoxPayload {
  name?: string
  description?: string
  entries?: { item_type: string; amount: number; chance: number; item_id?: string | null }[]
  is_active?: boolean
}

export interface LootBoxSimResult {
  drop_type: string
  item_id: string | null
  item_name: string | null
  total_dropped: number
  percentage: number
  total_xgen: number | null
  total_fragments: number | null
}

export interface AdminStarsPackage {
  id: string
  stars_amount: number
  xgen_reward: number
  is_active: boolean
}

export interface UpdateAdminStarsPackagePayload {
  stars_amount?: number
  xgen_reward?: number
  is_active?: boolean
}

export interface AdminSeason {
  id: string
  name: string
  description: string
  start_date: string
  end_date: string
  reward_xgen: number
  reward_fragments: number
  is_active: boolean
}

export interface CreateAdminSeasonPayload {
  name: string
  description: string
  start_date: string
  end_date: string
  reward_xgen?: number
  reward_fragments?: number
  is_active?: boolean
}

export interface UpdateAdminSeasonPayload {
  name?: string
  description?: string
  start_date?: string
  end_date?: string
  reward_xgen?: number
  reward_fragments?: number
  is_active?: boolean
}

export interface AdminPaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AdminShopBundleItem {
  item_id: string
  quantity: number
}

export interface AdminShopAnalytics {
  total_purchases: number
  today_purchases: number
  revenue_xgen: number
}

export interface AdminArticle {
  id: string
  chapter_id: string
  title: string
  content: string | null
  is_unlocked: boolean
  fragment_cost: number
  trigger_event_type: string | null
  trigger_threshold: number
  required_item_id?: string | null
  sort_order?: number
}

export interface ChapterRewardItem {
  item_id: string
  quantity: number
}

export interface AdminChapter {
  id: string
  name: string
  description: string
  is_secret: boolean
  season_id: string | null
  reward_xgen: number
  reward_fragments: number
  reward_items: ChapterRewardItem[]
  articles: AdminArticle[]
}

export interface AdminShopItem {
  id: string
  item_id: string | null
  price_xgen: number
  daily_limit: number
  stock_limit: number
  is_active: boolean
  bundle_items: AdminShopBundleItem[]
  analytics: AdminShopAnalytics
}

export interface CreateAdminShopItemPayload {
  item_id?: string
  price_xgen: number
  daily_limit?: number
  stock_limit?: number
  is_active?: boolean
  bundle_items?: AdminShopBundleItem[]
}

export interface UpdateAdminShopItemPayload {
  price_xgen?: number
  daily_limit?: number
  stock_limit?: number
  is_active?: boolean
  bundle_items?: AdminShopBundleItem[]
}
