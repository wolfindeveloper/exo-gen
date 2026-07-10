import axios from 'axios'

import type { ClaimAchievementResponse, ClaimResult, Expedition, GuideChapterDetail, GuideChaptersResponse, GuideClaimRewardResponse, GuideFixGlitchResponse, GuideResearchResponse, InventoryItem, Ship, ShipActionResponse, ShopBuyResponse, ShopItem, UserProfile, UserStats, Zone, ItemReference, AdminItem, AdminItemsResponse, CreateItemPayload, UpdateItemPayload, AdminZone, AdminZonesResponse, CreateZonePayload, UpdateZonePayload, AdminLootBox, CreateLootBoxPayload, UpdateLootBoxPayload, LootBoxSimResult, AdminShopItem, CreateAdminShopItemPayload, UpdateAdminShopItemPayload, AdminSeason, CreateAdminSeasonPayload, UpdateAdminSeasonPayload, AdminPaginatedResponse, AdminStarsPackage, UpdateAdminStarsPackagePayload, AdminChapter, AdminArticle, ChapterRewardItem } from '../types'

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '')

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

function zoneFromDTO(data: { id: string; name: string; description: string; image_url: string; fuel_cost: number; optimism_risk: number; duration_seconds: number; loot_table: { drop_type: string; amount: number; chance: number; item_id: string | null; item_name?: string | null }[]; tier?: number }): Zone {
  return {
    id: data.id,
    name: data.name,
    description: data.description,
    image_url: data.image_url,
    fuel_cost: data.fuel_cost,
    optimism_risk: data.optimism_risk,
    duration_seconds: data.duration_seconds,
    tier: data.tier ?? 1,
    loot_table: (data.loot_table || []).map((l) => ({
      item_id: l.item_id || null,
      item_type: l.drop_type || '',
      amount: l.amount || 1,
      chance: l.chance || 0,
      item_name: l.item_name || null,
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
    const data = await apiClient.get<{ items: { item: { id: string; name: string; description: string; type: string; rarity: string; effect: Record<string, unknown>; is_tradable: boolean; sell_price: number; image_url: string }; quantity: number }[] }>('/inventory').then((r) => r.data)
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
    const data = await apiClient.get<Expedition | null>('/expeditions/active').then((r) => r.data)
    return data ? [data] : []
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
    const data = await apiClient.post<{ xgen_earned: number; fragments_earned: number; items_earned: { item_id: string; amount: number; name?: string | null }[]; optimism_lost: number; current_tea: number; current_optimism: number }>('/expeditions/claim', { expedition_id: expeditionId }).then((r) => r.data)
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
    const data = await apiClient.get<{ id: string; name: string; description: string; image_url: string; fuel_cost: number; optimism_risk: number; duration_seconds: number; loot_table: { drop_type: string; amount: number; chance: number; item_id: string | null; item_name?: string | null }[] }[]>('/zones/').then((r) => r.data)
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
    return apiClient.post<{ newly_unlocked_articles: string[]; box_opened: boolean; box_xgen: number; box_fragments: number; box_items: Record<string, unknown>[] }>('/guide/trigger', { event_type: eventKey }).then((r) => r.data).catch(() => null)
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

  getAdminItems: async (page = 1, pageSize = 20, search?: string, sortBy?: string, sortOrder?: 'asc' | 'desc', rarity?: string) => {
    const params = new URLSearchParams()
    params.set('page', String(page))
    params.set('page_size', String(pageSize))
    if (search) params.set('search', search)
    if (sortBy) params.set('sort_by', sortBy)
    if (sortOrder) params.set('sort_order', sortOrder)
    if (rarity) params.set('rarity', rarity)
    const data = await apiClient.get<{ items: AdminItem[]; total: number; page: number; page_size: number; total_pages: number }>(
      `/admin/items?${params.toString()}`,
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

  getAdminZones: async (page = 1, pageSize = 20, search?: string, sortBy?: string, sortOrder?: 'asc' | 'desc') => {
    const params = new URLSearchParams()
    params.set('page', String(page))
    params.set('page_size', String(pageSize))
    if (search) params.set('search', search)
    if (sortBy) params.set('sort_by', sortBy)
    if (sortOrder) params.set('sort_order', sortOrder)
    const data = await apiClient.get<{ items: AdminZone[]; total: number; page: number; page_size: number; total_pages: number }>(
      `/admin/zones?${params.toString()}`,
    ).then((r) => r.data)
    return data as AdminZonesResponse
  },

  createAdminZone: async (payload: CreateZonePayload) => {
    const data = await apiClient.post<AdminZone>('/admin/zones', payload).then((r) => r.data)
    return data
  },

  updateAdminZone: async (id: string, payload: UpdateZonePayload) => {
    const data = await apiClient.patch<AdminZone>(`/admin/zones/${id}`, payload).then((r) => r.data)
    return data
  },

  deleteAdminZone: async (id: string) => {
    await apiClient.delete(`/admin/zones/${id}`)
  },

  getAdminLootBoxes: async () => {
    const data = await apiClient.get<AdminLootBox[]>('/admin/loot-boxes').then((r) => r.data)
    return data
  },

  createAdminLootBox: async (payload: CreateLootBoxPayload) => {
    const data = await apiClient.post<AdminLootBox>('/admin/loot-boxes', payload).then((r) => r.data)
    return data
  },

  updateAdminLootBox: async (id: string, payload: UpdateLootBoxPayload) => {
    const data = await apiClient.patch<AdminLootBox>(`/admin/loot-boxes/${id}`, payload).then((r) => r.data)
    return data
  },

  deleteAdminLootBox: async (id: string) => {
    await apiClient.delete(`/admin/loot-boxes/${id}`)
  },

  simulateLootBox: async (id: string, count: number) => {
    const data = await apiClient.post<LootBoxSimResult[]>(`/admin/loot-boxes/${id}/simulate`, { count }).then((r) => r.data)
    return data
  },

  simulateZone: async (zoneId: string, count: number) => {
    const data = await apiClient.post<LootBoxSimResult[]>(`/admin/zones/${zoneId}/simulate-loot`, { count }).then((r) => r.data)
    return data
  },

  getAdminShopItems: async () => {
    const data = await apiClient.get<AdminShopItem[]>('/admin/shop-items').then((r) => r.data)
    return data
  },

  createAdminShopItem: async (payload: CreateAdminShopItemPayload) => {
    const data = await apiClient.post('/admin/shop-items', payload).then((r) => r.data)
    return data
  },

  updateAdminShopItem: async (id: string, payload: UpdateAdminShopItemPayload) => {
    const data = await apiClient.patch(`/admin/shop-items/${id}`, payload).then((r) => r.data)
    return data
  },

  deleteAdminShopItem: async (id: string) => {
    await apiClient.delete(`/admin/shop-items/${id}`)
  },

  getAdminSeasons: async (page = 1, pageSize = 20, search?: string, sortBy?: string, sortOrder?: 'asc' | 'desc') => {
    const params = new URLSearchParams()
    params.set('page', String(page))
    params.set('page_size', String(pageSize))
    if (search) params.set('search', search)
    if (sortBy) params.set('sort_by', sortBy)
    if (sortOrder) params.set('sort_order', sortOrder)
    const data = await apiClient.get<AdminPaginatedResponse<AdminSeason>>(`/admin/seasons?${params.toString()}`).then((r) => r.data)
    return data
  },

  createAdminSeason: async (payload: CreateAdminSeasonPayload) => {
    const data = await apiClient.post<AdminSeason>('/admin/seasons', payload).then((r) => r.data)
    return data
  },

  updateAdminSeason: async (id: string, payload: UpdateAdminSeasonPayload) => {
    const data = await apiClient.patch<AdminSeason>(`/admin/seasons/${id}`, payload).then((r) => r.data)
    return data
  },

  deleteAdminSeason: async (id: string) => {
    await apiClient.delete(`/admin/seasons/${id}`)
  },

  getAdminStarsPackages: async (page = 1, pageSize = 20, search?: string, sortBy?: string, sortOrder?: 'asc' | 'desc') => {
    const params = new URLSearchParams()
    params.set('page', String(page))
    params.set('page_size', String(pageSize))
    if (search) params.set('search', search)
    if (sortBy) params.set('sort_by', sortBy)
    if (sortOrder) params.set('sort_order', sortOrder)
    const data = await apiClient.get<AdminPaginatedResponse<AdminStarsPackage>>(`/admin/stars-packages?${params.toString()}`).then((r) => r.data)
    return data
  },

  createAdminStarsPackage: async (payload: { stars_amount: number; xgen_reward: number; is_active: boolean }) => {
    const data = await apiClient.post<AdminStarsPackage>('/admin/stars-packages', payload).then((r) => r.data)
    return data
  },

  updateAdminStarsPackage: async (id: string, payload: UpdateAdminStarsPackagePayload) => {
    const data = await apiClient.patch<AdminStarsPackage>(`/admin/stars-packages/${id}`, payload).then((r) => r.data)
    return data
  },

  deleteAdminStarsPackage: async (id: string) => {
    await apiClient.delete(`/admin/stars-packages/${id}`)
  },

  getAdminChapters: async (page = 1, pageSize = 50, search?: string, sortBy?: string, sortOrder?: 'asc' | 'desc') => {
    const params = new URLSearchParams()
    params.set('page', String(page))
    params.set('page_size', String(pageSize))
    if (search) params.set('search', search)
    if (sortBy) params.set('sort_by', sortBy)
    if (sortOrder) params.set('sort_order', sortOrder)
    const data = await apiClient.get<AdminPaginatedResponse<AdminChapter>>(`/admin/chapters?${params.toString()}`).then((r) => r.data)
    return data
  },

  createAdminChapter: async (payload: { name: string; description: string; is_secret?: boolean; season_id?: string | null; reward_xgen?: number; reward_fragments?: number; reward_items?: ChapterRewardItem[] }) => {
    const data = await apiClient.post<AdminChapter>('/admin/chapters', payload).then((r) => r.data)
    return data
  },

  updateAdminChapter: async (id: string, payload: { name?: string; description?: string; is_secret?: boolean; reward_xgen?: number; reward_fragments?: number; reward_items?: ChapterRewardItem[] }) => {
    const data = await apiClient.patch<AdminChapter>(`/admin/chapters/${id}`, payload).then((r) => r.data)
    return data
  },

  deleteAdminChapter: async (id: string) => {
    await apiClient.delete(`/admin/chapters/${id}`)
  },

  createAdminArticle: async (payload: { chapter_id: string; title: string; content: string; fragment_cost?: number; trigger_event_type?: string | null; trigger_threshold?: number; required_item_id?: string | null }) => {
    const data = await apiClient.post<AdminArticle>('/admin/articles', payload).then((r) => r.data)
    return data
  },

  updateAdminArticle: async (id: string, payload: { title?: string; content?: string; fragment_cost?: number; trigger_event_type?: string | null; trigger_threshold?: number; required_item_id?: string | null }) => {
    const data = await apiClient.patch<AdminArticle>(`/admin/articles/${id}`, payload).then((r) => r.data)
    return data
  },

  deleteAdminArticle: async (id: string) => {
    await apiClient.delete(`/admin/articles/${id}`)
  },

  reorderChapterArticles: async (chapterId: string, articleIds: string[]) => {
    await apiClient.patch(`/admin/chapters/${chapterId}/reorder-articles`, articleIds)
  },
}
