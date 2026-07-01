import axios from 'axios'

import type { ClaimAchievementResponse, ClaimResult, Expedition, GuideChapterDetail, GuideChaptersResponse, GuideClaimRewardResponse, GuideFixGlitchResponse, GuideResearchResponse, InventoryItem, Ship, ShipActionResponse, ShopBuyResponse, ShopItem, UserProfile, UserStats, Zone, ItemReference, AdminItem, AdminItemsResponse, CreateItemPayload, UpdateItemPayload } from '../types'

const API_URL = (import.meta.env.VITE_API_URL || 'https://api.exo-gen.com').replace(/\/+$/, '')

export const apiClient = axios.create({
  baseURL: API_URL,
})

apiClient.interceptors.request.use((config) => {
  const initData = window.Telegram?.WebApp?.initData || ''
  console.log('[API Request]', config.url, 'InitData:', initData ? 'Exists' : 'EMPTY')
  if (initData) {
    config.headers['Authorization'] = `tghash ${initData}`
  }
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail || err.message || 'Request failed'
    const error = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    ;(error as Error & { status?: number }).status = err.response?.status
    return Promise.reject(error)
  },
)

function shipFromDTO(data: { id: string; name: string; tea_level: number; optimism: number; speed: number; defense: number; luck: number }): Ship {
  return {
    id: data.id,
    name: data.name,
    tea_level: data.tea_level,
    optimism: data.optimism,
    speed: data.speed,
    defense: data.defense,
    luck: data.luck,
  }
}

function zoneFromDTO(data: { id: string; name: string; description: string; image_url: string; fuel_cost: number; optimism_risk: number; duration_seconds: number; loot_table: { item_type: string; amount: number; chance: number; item_id: string | null }[] }): Zone {
  return {
    id: data.id,
    name: data.name,
    description: data.description,
    image_url: data.image_url,
    fuel_cost: data.fuel_cost,
    optimism_risk: data.optimism_risk,
    duration_seconds: data.duration_seconds,
    loot_table: (data.loot_table || []).map((l) => ({
      item_id: l.item_id || null,
      item_type: l.item_type || '',
      amount: l.amount || 1,
      chance: l.chance || 0,
    })),
  }
}

export const api = {
  health: () => apiClient.get<{ status: string }>('/health').then((r) => r.data),

  authInit: async () => {
    const initData = window.Telegram?.WebApp?.initData || ''
    if (!initData) {
      console.error('Telegram context is not available')
      throw new Error('Telegram context is not available')
    }
    const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user as { id: number; first_name?: string; username?: string; language_code?: string } | undefined
    if (tgUser) {
      await apiClient.post('/players/register', {
        telegram_id: tgUser.id,
        username: tgUser.username || tgUser.first_name || '',
        language_code: tgUser.language_code || 'en',
      }).catch(() => {})
    }
    const [me, profile] = await Promise.all([
      apiClient.get<{ id: string; telegram_id: number; username: string | null; xp: number; xgen_balance: number; fragments_balance: number; daily_streak: number; ship_count: number; ship_id: string }>('/players/me').then((r) => r.data),
      apiClient.get<{ xp: number; level: number; total_expeditions: number; total_artifacts_found: number; unlocked_articles: number }>('/players/me/profile').then((r) => r.data).catch(() => null),
    ])
    return {
      ...me,
      level: profile?.level ?? 1,
      balance_stars: 0,
      daily_reward: false,
      streak_broken: false,
      daily_reward_items: {},
    } as UserProfile & { is_new?: boolean; box_rewards?: Record<string, unknown> }
  },

  getProfile: async () => {
    const [me, profile] = await Promise.all([
      apiClient.get<{ id: string; telegram_id: number; username: string | null; xp: number; xgen_balance: number; fragments_balance: number; daily_streak: number; ship_count: number; ship_id: string }>('/players/me').then((r) => r.data),
      apiClient.get<{ xp: number; level: number; total_expeditions: number; total_artifacts_found: number; unlocked_articles: number }>('/players/me/profile').then((r) => r.data).catch(() => null),
    ])
    return {
      ...me,
      level: profile?.level ?? 1,
      balance_stars: 0,
      daily_reward: false,
      streak_broken: false,
      daily_reward_items: {},
    } as UserProfile
  },

  checkAdminStatus: async () => {
    const data = await apiClient.get<{ is_admin: boolean }>('/players/me/admin-status').then((r) => r.data)
    return data.is_admin
  },

  getInventory: async () => {
    const data = await apiClient.get<{ items: { item: { id: string; name: string; description: string; type: string; rarity: string; effect: Record<string, unknown>; is_tradable: boolean; sell_price: number }; quantity: number }[] }>('/inventory').then((r) => r.data)
    return data.items.map((i) => ({
      item: i.item as ItemReference,
      quantity: i.quantity,
    })) as InventoryItem[]
  },

  getShips: async () => {
    const data = await apiClient.get<{ id: string; name: string; tea_level: number; optimism: number; speed: number; defense: number; luck: number }>('/ships/me').then((r) => r.data)
    return [shipFromDTO(data)]
  },

  getActiveExpeditions: async () => {
    return []
  },

  startExpedition: async (zoneId: string) => {
    const me = await apiClient.get<{ ship_id: string }>('/players/me').then((r) => r.data)
    const data = await apiClient.post<{ id: string; ship_id: string; zone_id: string; started_at: string; ends_at: string; status: string; remaining_tea: number }>('/expeditions/start', { ship_id: me.ship_id, zone_id: zoneId }).then((r) => r.data)
    return {
      id: data.id,
      ship_id: data.ship_id,
      zone_id: data.zone_id,
      started_at: data.started_at,
      ends_at: data.ends_at,
      status: data.status,
      remaining_tea: data.remaining_tea,
    } as Expedition
  },

  claimExpedition: async (expeditionId: string) => {
    const data = await apiClient.post<{ xgen_earned: number; fragments_earned: number; items_earned: { item_id: string; amount: number }[]; optimism_lost: number; current_tea: number; current_optimism: number }>('/expeditions/claim', { expedition_id: expeditionId }).then((r) => r.data)
    return {
      xgen_earned: data.xgen_earned,
      fragments_earned: data.fragments_earned,
      items_earned: data.items_earned,
      optimism_lost: data.optimism_lost,
      current_tea: data.current_tea,
      current_optimism: data.current_optimism,
    } as ClaimResult
  },

  getStats: async () => {
    const data = await apiClient.get<{ xp: number; level: number; total_expeditions: number; total_artifacts_found: number; unlocked_articles: number }>('/players/me/profile').then((r) => r.data)
    return {
      total_expeditions: data.total_expeditions,
      completed_expeditions: data.total_expeditions,
      failed_expeditions: 0,
      artifacts_crafted: 0,
      joined_days: 0,
      total_xp_earned: data.xp,
      zones_explored: data.total_expeditions,
      equipped_artifacts_count: 0,
      unique_artifacts: data.total_artifacts_found,
      resources: { fuel: 0, repair_kits: 0 },
      guide_progress: { total_chapters: 0, completed_chapters: 0, entries_researched: data.unlocked_articles },
      recent_expeditions: [],
      glitches_fixed: 0,
      total_purchases: 0,
    } as UserStats
  },

  updateProfile: async (_data: { username?: string; add_xgen?: number }) => {
    const me = await apiClient.get<{ id: string; telegram_id: number; username: string | null; xp: number; xgen_balance: number; fragments_balance: number; daily_streak: number; ship_count: number; ship_id: string }>('/players/me').then((r) => r.data)
    return {
      ...me,
      level: 1,
      balance_stars: 0,
      daily_reward: false,
      streak_broken: false,
      daily_reward_items: {},
    } as UserProfile
  },

  refuelShip: async (shipId: string, _resourceId: string) => {
    await apiClient.post<{ message: string; item_used_id: string; item_used_name: string; tea_restored: number; new_tea_level: number }>('/ships/refuel', { ship_id: shipId })
    const shipData = await apiClient.get<{ id: string; name: string; tea_level: number; optimism: number; speed: number; defense: number; luck: number }>('/ships/me').then((r) => r.data)
    const inv = await apiClient.get<{ items: { item: ItemReference; quantity: number }[] }>('/inventory').then((r) => r.data)
    return { ship: shipFromDTO(shipData), inventory: inv.items as InventoryItem[] } as ShipActionResponse
  },

  repairShip: async (shipId: string, _resourceId: string) => {
    await apiClient.post<{ message: string; item_used_id: string; item_used_name: string; optimism_restored: number; new_optimism_level: number }>('/ships/repair', { ship_id: shipId })
    const shipData = await apiClient.get<{ id: string; name: string; tea_level: number; optimism: number; speed: number; defense: number; luck: number }>('/ships/me').then((r) => r.data)
    const inv = await apiClient.get<{ items: { item: ItemReference; quantity: number }[] }>('/inventory').then((r) => r.data)
    return { ship: shipFromDTO(shipData), inventory: inv.items as InventoryItem[] } as ShipActionResponse
  },

  equipSlot: async (_shipId: string, _slotIndex: number, _artifactId: string) => {
    const shipData = await apiClient.get<{ id: string; name: string; tea_level: number; optimism: number; speed: number; defense: number; luck: number }>('/ships/me').then((r) => r.data)
    const inv = await apiClient.get<{ items: { item: ItemReference; quantity: number }[] }>('/inventory').then((r) => r.data)
    return { ship: shipFromDTO(shipData), inventory: inv.items as InventoryItem[] } as ShipActionResponse
  },

  unequipSlot: async (_shipId: string, _slotIndex: number) => {
    const shipData = await apiClient.get<{ id: string; name: string; tea_level: number; optimism: number; speed: number; defense: number; luck: number }>('/ships/me').then((r) => r.data)
    const inv = await apiClient.get<{ items: { item: ItemReference; quantity: number }[] }>('/inventory').then((r) => r.data)
    return { ship: shipFromDTO(shipData), inventory: inv.items as InventoryItem[] } as ShipActionResponse
  },

  getShipsContent: async () => {
    return []
  },

  getZonesContent: async () => {
    const data = await apiClient.get<{ id: string; name: string; description: string; image_url: string; fuel_cost: number; optimism_risk: number; duration_seconds: number; loot_table: { item_type: string; amount: number; chance: number; item_id: string | null }[] }[]>('/zones/').then((r) => r.data)
    return data.map(zoneFromDTO)
  },

  getResourcesContent: async () => {
    return []
  },

  getArtifactsContent: async () => {
    return []
  },

  getRanksContent: async () => {
    return []
  },

  getGuideChapters: async () => {
    const data = await apiClient.get<{ chapters: { id: string; name: string; description: string; is_secret: boolean; season_id: string | null; reward_xgen: number; reward_fragments: number; reward_items: Record<string, unknown>[]; articles: { id: string; chapter_id: string; title: string; content: string | null; is_unlocked: boolean; fragment_cost: number; trigger_event_type: string | null; trigger_threshold: number }[] }[]; player_fragments_balance: number }>('/guide/').then((r) => r.data)
    return {
      chapters: data.chapters.map((ch) => ({
        id: ch.id,
        title: ch.name,
        description: ch.description,
        order: 0,
        is_secret: ch.is_secret,
        reward_artifact_id: '',
        total_entries: ch.articles.length,
        researched_count: ch.articles.filter((a) => a.is_unlocked).length,
        all_researched: ch.articles.every((a) => a.is_unlocked),
        reward_claimed: false,
        entries: ch.articles.map((a) => ({
          id: a.id,
          title: a.title,
          fragment_cost: a.fragment_cost,
          status: a.is_unlocked ? 'researched' as const : 'locked' as const,
          has_event: !!a.trigger_event_type,
          unlock_event: a.trigger_event_type,
        })),
      })),
    } as GuideChaptersResponse
  },

  getGuideChapter: async (chapterId: string) => {
    const data = await apiClient.get<{ chapters: { id: string; name: string; description: string; is_secret: boolean; season_id: string | null; reward_xgen: number; reward_fragments: number; reward_items: Record<string, unknown>[]; articles: { id: string; chapter_id: string; title: string; content: string | null; is_unlocked: boolean; fragment_cost: number; trigger_event_type: string | null; trigger_threshold: number }[] }[]; player_fragments_balance: number }>('/guide/').then((r) => r.data)
    const ch = data.chapters.find((c) => c.id === chapterId)
    if (!ch) throw new Error('Chapter not found')
    return {
      id: ch.id,
      title: ch.name,
      description: ch.description,
      is_secret: ch.is_secret,
      reward_artifact_id: '',
      total_entries: ch.articles.length,
      researched_count: ch.articles.filter((a) => a.is_unlocked).length,
      all_researched: ch.articles.every((a) => a.is_unlocked),
      reward_claimed: false,
      entries: ch.articles.map((a) => ({
        id: a.id,
        title: a.title,
        fragment_cost: a.fragment_cost,
        status: a.is_unlocked ? 'researched' as const : 'locked' as const,
        has_event: !!a.trigger_event_type,
        unlock_event: a.trigger_event_type,
        text: a.content,
        glitch_chance: 0,
      })),
    } as GuideChapterDetail
  },

  researchEntry: async (_chapterId: string, entryId: string) => {
    const data = await apiClient.post<{ content: string; new_fragments_balance: number; chapter_completed: boolean; xgen_rewarded: number; fragments_rewarded: number; box_opened: boolean; box_xgen: number; box_fragments: number; box_items: Record<string, unknown>[] }>('/guide/unlock', { article_id: entryId }).then((r) => r.data)
    return { status: 'ok', fixed: true, balance_fragments: data.new_fragments_balance } as GuideResearchResponse
  },

  fixGlitch: async (_chapterId: string, _entryId: string) => {
    return { status: 'ok', balance_fragments: 0 } as GuideFixGlitchResponse
  },

  claimReward: async (_chapterId: string) => {
    return { status: 'ok', artifact_id: '', artifact_name: '' } as GuideClaimRewardResponse
  },

  logEvent: async (eventKey: string) => {
    await apiClient.post('/guide/trigger', { event_type: eventKey }).catch(() => {})
    return { status: 'ok' }
  },

  getShopCatalog: async () => {
    const data = await apiClient.get<{ id: string; item_id: string; price_xgen: number; daily_limit: number; stock_limit: number; is_active: boolean }[]>('/shop/').then((r) => r.data)
    return data.map((s) => ({
      id: s.id,
      category: 'resources',
      name_key: '',
      description_key: '',
      price: { amount: s.price_xgen, currency: 'xgen' as const },
      rewards: [{ type: 'item', item_config_id: s.item_id }],
      icon_path: undefined,
    })) as ShopItem[]
  },

  buyShopItem: async (itemId: string) => {
    const data = await apiClient.post<{ success: boolean; message: string; item_id: string | null; quantity: number; xgen_spent: number }>('/shop/purchase', { shop_item_id: itemId }).then((r) => r.data)
    return {
      status: data.success ? 'ok' : 'error',
      granted: data.item_id ? [{ type: 'item', item_config_id: data.item_id, quantity: data.quantity }] : [],
      balance_xgen: 0,
      balance_stars: 0,
    } as ShopBuyResponse
  },

  getAchievements: async () => {
    return []
  },

  claimAchievement: async (achievementId: string) => {
    return { status: 'ok', achievement_id: achievementId, xp_gained: 0, xgen_gained: 0 } as ClaimAchievementResponse
  },

  getAdminItems: async (page = 1, pageSize = 50) => {
    const data = await apiClient.get<{ items: AdminItem[]; total: number; page: number; page_size: number; total_pages: number }>(
      `/admin/items?page=${page}&page_size=${pageSize}`,
    ).then((r) => r.data)
    return data as AdminItemsResponse
  },

  createAdminItem: async (payload: CreateItemPayload) => {
    const data = await apiClient.post<AdminItem>('/admin/items', payload).then((r) => r.data)
    return data
  },

  updateAdminItem: async (id: string, payload: UpdateItemPayload) => {
    const data = await apiClient.patch<AdminItem>(`/admin/items/${id}`, payload).then((r) => r.data)
    return data
  },

  deleteAdminItem: async (id: string) => {
    await apiClient.delete(`/admin/items/${id}`)
  },
}
