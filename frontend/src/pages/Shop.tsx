import { useCallback, useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { AlertTriangle, Diamond, Gift, Package, ShoppingBag, Star } from 'lucide-react'

import { api } from '../api/client'
import { MysteryBoxPreview } from '../components/MysteryBoxPreview'
import BundlePreviewModal from '../components/BundlePreviewModal'
import { Skeleton } from '../components/Skeleton'
import { PullToRefresh } from '../components/PullToRefresh'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { useGameStore } from '../store/game'
import { statLabels } from '../lib/stats'
import { hapticImpact } from '../lib/telegram'
import type { ShopBuyResponse, ShopCategory, ShopItem } from '../types'

interface CoinParticle {
  id: number
  x: number
  y: number
  tx: number
  ty: number
  emoji: string
}

let coinId = 0

const rarityConfig: Record<string, { color: string; label: string }> = {
  common: { color: 'text-slate-400', label: 'C' },
  uncommon: { color: 'text-green-400', label: 'U' },
  rare: { color: 'text-blue-400', label: 'R' },
  epic: { color: 'text-purple-400', label: 'E' },
  legendary: { color: 'text-amber-400', label: 'L' },
}

const tierNames: Record<number, string> = {
  1: 'Ранг I',
  2: 'Ранг II',
  3: 'Ранг III',
  4: 'Ранг IV',
  5: 'Ранг V',
}

const sellerComments: Record<string, string[]> = {
  fuel_pack: ['«Разумный выбор. Редкость.»', '«Пейте, космонавты, заварку — в космосе она бесполезна, но согревает душу.»'],
  repair_pack: ['«Оптимизм — это вам не прочность. Но звучит лучше.»', '«Купил — починился. Не починился — купи ещё.»'],
  fragment_pack: ['«Бред — он и в галактике бред.»', '«20 фрагментов. 20 шансов запутаться ещё сильнее.»'],
  mystery_box: ['«Никто не знает, что там. Даже я. Особенно я.»', '«Может там артефакт. А может там записка «купи ещё». Спекуляция!»'],
  instant_finish: ['«Срезать углы? В космосе нет углов. Но мы их придумаем за 3 звезды.»', '«Мгновенно. Почти. Как и всё в этой вселенной.'],
}

const artifactComments: Record<number, string[]> = {
  1: ['«Начальный уровень. Как первая работа.»', '«T1 — это вам не T2. Но и не T0. А T0 нет.»'],
  2: ['«Уже что-то. Почти.»', '«Второй ранг. Звучит лучше, чем «почти легендарка».»'],
  3: ['«Редкость. Как честный политик.»', '«T3. Золотая середина между «дешево» и «дорого».»'],
  4: ['«Эпик. Вы либо везунчик, либо транжира.»', '«T4. Если не работает — попробуйте перезагрузить вселенную.»'],
  5: ['«Легендарно. Поздравляю. Вы разорились.»', '«T5. Единственное, что легендарнее этого артефакта — ваша способность тратить звёзды.»'],
}

function getComment(item: ShopItem): string | null {
  if (item.type === 'artifact' && item.tier) {
    const pool = artifactComments[item.tier]
    if (!pool) return null
    return pool[Math.floor(Math.random() * pool.length)]
  }
  const pool = sellerComments[item.id]
  if (!pool) return null
  return pool[Math.floor(Math.random() * pool.length)]
}

function SellerComment({ item, visible }: { item: ShopItem; visible: boolean }) {
  const comment = getComment(item)
  if (!comment) return null
  return (
    <AnimatePresence>
      {visible && (
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          className="text-[10px] text-amber-600/60 italic mt-2 leading-relaxed text-center"
        >
          {comment}
        </motion.p>
      )}
    </AnimatePresence>
  )
}

function StatBadge({ label, value }: { label: string; value: number }) {
  return (
    <span className="inline-flex items-center gap-1 text-[9px] text-slate-500 bg-white/5 px-1.5 py-0.5 rounded-md">
      <span className="text-[9px]">{statLabels[label] || label}</span>
      <span className={value > 0 ? 'text-neon-cyan' : 'text-slate-500'}>
        {value > 0 ? '+' : ''}{value}
      </span>
    </span>
  )
}

function ArtifactCard({
  item,
  canAfford,
  isBuying,
  onBuy,
  buyerCommentVisible,
}: {
  item: ShopItem
  canAfford: boolean
  isBuying: boolean
  onBuy: (e: React.MouseEvent) => void
  buyerCommentVisible: boolean
}) {
  const rarity = rarityConfig[item.rarity ?? 'common'] ?? rarityConfig.common
  const stats = item.stats_modifiers ?? {}
  const isStars = item.price.currency === 'stars'

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 24 }}
      className="rounded-xl border border-white/5 bg-space-800/60 p-3.5 space-y-2"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          {item.icon_path ? (
            <img src={item.icon_path} alt={item.name_key} className="shrink-0 w-10 h-10 rounded-lg object-cover" />
          ) : (
            <div className={`shrink-0 w-10 h-10 rounded-lg border flex items-center justify-center ${rarity.color.replace('text', 'border')}/30 bg-black/30`}>
              <Diamond size={16} className={rarity.color} />
            </div>
          )}
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-[9px] font-bold ${rarity.color} px-1 py-0.5 rounded border ${rarity.color.replace('text', 'border')}/30 leading-none`}>
                {rarity.label}
              </span>
              <span className="text-[9px] text-slate-600 font-mono">{tierNames[item.tier ?? 1]}</span>
              <h3 className="font-display text-xs text-slate-200 uppercase tracking-wider truncate">
                {item.name_key || 'Предмет'}
              </h3>
            </div>
            <p className="text-[10px] text-slate-500 mt-1 leading-relaxed line-clamp-2">
              {item.description_key || 'Описание отсутствует'}
            </p>
            {Object.keys(stats).length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1.5">
                {Object.entries(stats).map(([key, val]) => (
                  <StatBadge key={key} label={key} value={val} />
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="shrink-0 text-right">
          <span className={`font-display text-sm tabular-nums ${isStars ? 'text-amber-400' : 'text-neon-cyan'}`}>
            {item.price.amount}
          </span>
          <span className={`text-[10px] ml-0.5 ${isStars ? 'text-amber-400' : 'text-neon-cyan'}`}>
            {isStars ? '⭐' : '✦'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onBuy}
          disabled={!canAfford || isBuying}
          className={`flex-1 py-2 rounded-lg text-[10px] font-display uppercase tracking-wider transition-all ${
            isBuying
              ? 'bg-slate-700/50 text-slate-500'
              : canAfford
                ? 'bg-white/5 text-slate-300 border border-white/10 hover:bg-white/10 active:scale-[0.97]'
                : 'bg-slate-800/50 text-slate-700 border border-slate-700/30 cursor-not-allowed'
          }`}
        >
          {isBuying ? (
            <span className="flex items-center justify-center gap-1">
              <motion.span animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                <Package size={12} />
              </motion.span>
              Обрабатываем...
            </span>
          ) : canAfford ? (
            'Приобрести'
          ) : (
            'Не хватает'
          )}
        </button>
      </div>

      <SellerComment item={item} visible={buyerCommentVisible} />
    </motion.div>
  )
}

function BundleCard({
  item,
  canAfford,
  isBuying,
  onBuy,
  onPreview,
}: {
  item: ShopItem
  canAfford: boolean
  isBuying: boolean
  onBuy: () => void
  onPreview: () => void
}) {
  const itemCount = item.bundle_items_info?.length || 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 24 }}
      className="rounded-xl border border-amber-500/20 bg-gradient-to-br from-amber-500/5 to-yellow-500/5 p-4 space-y-3"
    >
      <div className="flex items-start gap-3">
        <div className="shrink-0 w-14 h-14 rounded-xl border border-amber-500/20 bg-black/30 flex items-center justify-center overflow-hidden">
          {item.bundle_image_url ? (
            <img src={item.bundle_image_url} alt={item.bundle_name} className="w-full h-full object-cover" />
          ) : (
            <Package size={24} className="text-amber-400" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[8px] font-display uppercase tracking-wider px-1.5 py-0.5 rounded border border-amber-500/30 text-amber-400 bg-amber-500/10">
              {'\u041d\u0430\u0431\u043e\u0440'}
            </span>
            <span className="text-[9px] text-slate-500">
              {itemCount} {itemCount === 1 ? '\u043f\u0440\u0435\u0434\u043c\u0435\u0442' : '\u043f\u0440\u0435\u0434\u043c\u0435\u0442\u043e\u0432'}
            </span>
          </div>
          <h3 className="font-display text-sm text-amber-300 uppercase tracking-wider truncate">
            {item.bundle_name || item.name_key}
          </h3>
          {item.bundle_description && (
            <p className="text-[10px] text-slate-500 mt-1 leading-relaxed line-clamp-2">
              {item.bundle_description}
            </p>
          )}
        </div>

        <div className="shrink-0 text-right">
          <span className="font-display text-sm tabular-nums text-amber-400">
            {item.price.amount}
          </span>
          <span className="text-[10px] ml-0.5 text-amber-400">{'\u2726'}</span>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={onPreview}
          className="flex-1 py-2 rounded-lg text-[10px] font-display uppercase tracking-wider bg-white/5 text-slate-300 border border-white/10 hover:bg-white/10 active:scale-[0.97] transition-all"
        >
          {'\u{1F4CB} \u0427\u0442\u043e \u0432\u043d\u0443\u0442\u0440\u0438'}
        </button>
        <button
          onClick={onBuy}
          disabled={!canAfford || isBuying}
          className={`flex-1 py-2 rounded-lg text-[10px] font-display uppercase tracking-wider transition-all ${
            isBuying
              ? 'bg-slate-700/50 text-slate-500'
              : canAfford
                ? 'bg-gradient-to-r from-amber-500/20 to-yellow-500/20 text-amber-400 border border-amber-500/25 active:scale-[0.97]'
                : 'bg-slate-800/50 text-slate-700 border border-slate-700/30 cursor-not-allowed'
          }`}
        >
          {isBuying ? '\u041f\u043e\u043a\u0443\u043f\u0430\u0435\u043c...' : canAfford ? '\u041f\u0440\u0438\u043e\u0431\u0440\u0435\u0441\u0442\u0438' : '\u041d\u0435 \u0445\u0432\u0430\u0442\u0430\u0435\u0442'}
        </button>
      </div>
    </motion.div>
  )
}

export function Shop() {
  const loadProfile = useGameStore((s) => s.loadProfile)
  const loadInventory = useGameStore((s) => s.loadInventory)
  const user = useGameStore((s) => s.user)
  const isAdmin = useGameStore((s) => s.isAdmin)

  const [items, setItems] = useState<ShopItem[]>([])
  const [loading, setLoading] = useState(true)
  const [buying, setBuying] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [activeCategory, setActiveCategory] = useState('resources')
  const [buyerCommentItem, setBuyerCommentItem] = useState<ShopItem | null>(null)
  const [lastBuyResult, setLastBuyResult] = useState<{ shopItem: ShopItem; response: ShopBuyResponse } | null>(null)
  const [coinParticles, setCoinParticles] = useState<CoinParticle[]>([])
  const commentTimeout = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const [starsConfirmItem, setStarsConfirmItem] = useState<ShopItem | null>(null)
  const [xgenConfirmItem, setXgenConfirmItem] = useState<ShopItem | null>(null)
  const [bundlePreview, setBundlePreview] = useState<ShopItem | null>(null)
  const [starsPackages, setStarsPackages] = useState<{ id: string; stars_amount: number; xgen_reward: number; is_active: boolean }[]>([])
  const [shopCategories, setShopCategories] = useState<ShopCategory[]>([])

  useEffect(() => {
    api.getShopCategories()
      .then(setShopCategories)
      .catch(() => console.warn('Failed to load shop categories'))
  }, [])

  useEffect(() => {
    api.getStarsPackages()
      .then(setStarsPackages)
      .catch(() => console.warn('Failed to load stars packages'))
  }, [])

  useEffect(() => {
    api.getShopCatalog()
      .then(setItems)
      .catch(() => setError('Не удалось загрузить лавку'))
      .finally(() => setLoading(false))
  }, [])

  const handleRefresh = useCallback(async () => {
    setError(null)
    const [data, cats] = await Promise.all([api.getShopCatalog(), api.getShopCategories()])
    setItems(data)
    setShopCategories(cats)
  }, [])

  useEffect(() => {
    if (!successMsg) return
    const t2 = setTimeout(() => setSuccessMsg(null), 3500)
    return () => clearTimeout(t2)
  }, [successMsg])

  useEffect(() => {
    if (!buyerCommentItem) return
    clearTimeout(commentTimeout.current)
    commentTimeout.current = setTimeout(() => setBuyerCommentItem(null), 3000)
    return () => clearTimeout(commentTimeout.current)
  }, [buyerCommentItem])

  const shopItems = items.filter((i) => i.category === activeCategory && i.type !== 'artifact')
  const artifactItems = items.filter((i) => i.category === 'artifacts' && i.type === 'artifact')
  const isArtifactCategory = activeCategory === 'artifacts'

  const tabs = [
    ...shopCategories.map((c) => ({ key: c.slug, label: c.name, icon: c.icon })),
    { key: 'stars', label: 'Stars', icon: '⭐' },
  ]

  const executeBuy = useCallback(async (shopItem: ShopItem, btnEl?: HTMLElement) => {
    setBuying(shopItem.id)
    setError(null)
    try {
      const result = await api.buyShopItem(shopItem.id)
      hapticImpact('heavy')

      if (btnEl) {
        const rect = btnEl.getBoundingClientRect()
        const startX = rect.left + rect.width / 2
        const startY = rect.top
        const emojis = ['💎', '✦', '⭐', '💎', '✦', '💎', '⭐', '💎']
        const count = 5 + Math.floor(Math.random() * 4)
        const particles: CoinParticle[] = Array.from({ length: count }, (_, i) => ({
          id: ++coinId,
          x: startX + (Math.random() - 0.5) * 40,
          y: startY + (Math.random() - 0.5) * 20,
          tx: (Math.random() - 0.5) * 60,
          ty: -(80 + Math.random() * 120),
          emoji: emojis[i % emojis.length],
        }))
        setCoinParticles(particles)
        setTimeout(() => setCoinParticles([]), 700)
      }

      setSuccessMsg(shopItem.name_key)
      setBuyerCommentItem(shopItem)
      if (result.granted.length > 0) {
        setLastBuyResult({ shopItem, response: result })
      }
      await Promise.all([loadProfile(), loadInventory()])
    } catch (e) {
      hapticImpact('light')
      setTimeout(() => hapticImpact('light'), 100)
      setError((e as Error).message)
    } finally {
      setBuying(null)
    }
  }, [loadProfile, loadInventory])

  const handleBuy = useCallback(async (shopItem: ShopItem) => {
    if (shopItem.price.currency === 'stars') {
      setStarsConfirmItem(shopItem)
      return
    }
    setXgenConfirmItem(shopItem)
  }, [])

  const handleBuyStars = async (packageId: string) => {
    try {
      const result = await api.buyXgenWithStars(packageId)
      if (result.invoice_url) {
        window.open(result.invoice_url, '_blank')
      }
    } catch (e) {
      setError((e as Error).message)
    }
  }

  if (loading) {
    return (
      <div className="px-4 pt-4 pb-4 space-y-4">
        <div className="text-center space-y-2">
          <Skeleton variant="text" className="mx-auto w-48" />
          <Skeleton variant="text" className="mx-auto w-64" />
        </div>
        <div className="flex gap-1 justify-center">
          {Array.from({ length: 4 }, (_, i) => (
            <Skeleton key={i} variant="text" className="w-16 h-8 rounded-xl" />
          ))}
        </div>
        <Skeleton variant="card" count={4} />
      </div>
    )
  }

  return (
    <PullToRefresh onRefresh={handleRefresh}>
    <div className="px-4 pt-4 pb-4 space-y-4">
      <div className="text-center">
        <h1 className="font-display text-sm text-amber-400 uppercase tracking-[0.15em]">
          Спекулятивная лавка
        </h1>
        <p className="text-[10px] text-slate-600 mt-1 max-w-[260px] mx-auto leading-relaxed">
          «Мы не берём карты. Мы не берём наличные. Мы берём вашу веру в то, что эта сделка имеет смысл. Этого достаточно.»
        </p>
      </div>

      <div className="flex items-center justify-center gap-4 text-xs">
        <span className="text-neon-cyan font-mono">✦ {user?.xgen_balance ?? 0}</span>
        <span className="text-amber-400 font-mono">⭐ {user?.balance_stars ?? 0}</span>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 bg-red-900/20 border border-red-900/30 rounded-lg px-3 py-2"
          >
            <AlertTriangle size={14} className="text-red-400 shrink-0" />
            <span className="text-[11px] text-red-300">{error}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex gap-1 overflow-x-auto -mx-4 px-4 scrollbar-none">
        {tabs.map((tab) => {
          const active = activeCategory === tab.key
          return (
            <button
              key={tab.key}
              onClick={() => setActiveCategory(tab.key)}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-[10px] font-display uppercase tracking-wider transition-all shrink-0 ${
                active
                  ? 'bg-amber-500/15 text-amber-400 border border-amber-500/25'
                  : 'text-slate-600 hover:text-slate-400 border border-transparent'
              }`}
            >
              <span className="text-sm leading-none">{tab.icon}</span>
              {tab.label}
            </button>
          )
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeCategory}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.2 }}
          className="space-y-3"
        >
          {isArtifactCategory ? (
            artifactItems.length > 0 ? (
              [5, 4, 3, 2, 1].map((tier) => {
                const tierArtifacts = artifactItems.filter((a) => a.tier === tier)
                if (tierArtifacts.length === 0) return null
                return (
                  <div key={tier} className="space-y-2">
                    <div className="flex items-center gap-2 pt-1">
                      <div className="h-px flex-1 bg-white/5" />
                      <span className="text-[9px] text-slate-600 font-display uppercase tracking-widest">
                        {tierNames[tier]}
                      </span>
                      <div className="h-px flex-1 bg-white/5" />
                    </div>
                    {tierArtifacts.map((item) => {
                      const canAfford = item.price.currency === 'stars'
                        ? (user?.balance_stars ?? 0) >= item.price.amount
                        : (user?.xgen_balance ?? 0) >= item.price.amount
                      return (
                        <ArtifactCard
                          key={item.id}
                          item={item}
                          canAfford={canAfford}
                          isBuying={buying === item.id}
                          onBuy={() => handleBuy(item)}
                          buyerCommentVisible={buyerCommentItem?.id === item.id}
                        />
                      )
                    })}
                  </div>
                )
              })
            ) : (
              <div className="text-center py-8">
                <Diamond size={24} className="text-slate-700 mx-auto mb-2" />
                <p className="text-[11px] text-slate-600">Артефакты закончились</p>
              </div>
            )
          ) : activeCategory === 'stars' ? (
            starsPackages.length > 0 ? (
              <div className="space-y-3">
                <div className="text-center py-3">
                  <p className="text-[10px] text-amber-400/70 italic">
                    «Звёзды — это не просто валюта. Это способ сказать вселенной: "Я серьёзен".»
                  </p>
                </div>
                {starsPackages.map((pkg) => (
                  <motion.div
                    key={pkg.id}
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 24 }}
                    className="rounded-xl border border-amber-500/20 bg-gradient-to-br from-amber-500/10 to-yellow-500/5 p-4 space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
                          <Star size={24} className="text-amber-400" />
                        </div>
                        <div>
                          <h3 className="font-display text-sm text-amber-300 uppercase tracking-wider">
                            {pkg.xgen_reward.toLocaleString()} XGen
                          </h3>
                          <p className="text-[10px] text-slate-500 mt-0.5">
                            Мгновенное начисление
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="font-display text-lg text-amber-400 tabular-nums">
                          {pkg.stars_amount}
                        </span>
                        <span className="text-sm text-amber-400 ml-1">⭐</span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleBuyStars(pkg.id)}
                      className="w-full py-2.5 rounded-lg bg-gradient-to-r from-amber-500/30 to-yellow-500/30 text-amber-300 border border-amber-500/30 text-[11px] font-display uppercase tracking-wider hover:from-amber-500/40 hover:to-yellow-500/40 active:scale-[0.97] transition-all"
                    >
                      Купить за Stars
                    </button>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Star size={24} className="text-slate-700 mx-auto mb-2" />
                <p className="text-[11px] text-slate-600">Stars пакеты временно недоступны</p>
              </div>
            )
          ) : (
            shopItems.length === 0 ? (
              <div className="text-center py-8">
                <ShoppingBag size={24} className="text-slate-700 mx-auto mb-2" />
                <p className="text-[11px] text-slate-600 mb-3">В этой категории пока пусто</p>
                <motion.button
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => {
                    hapticImpact('light')
                    const otherTab = tabs.find((t) => t.key !== activeCategory)
                    setActiveCategory(otherTab?.key ?? 'stars')
                  }}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-neon-purple/10 border border-neon-purple/25 text-neon-purple text-[10px] font-display uppercase tracking-wider hover:bg-neon-purple/15 transition-colors"
                >
                  Посмотреть другие категории
                </motion.button>
              </div>
            ) : (
              shopItems.map((item) => {
              if (item.is_bundle) {
                const canAfford = (user?.xgen_balance ?? 0) >= item.price.amount
                return (
                  <BundleCard
                    key={item.id}
                    item={item}
                    canAfford={canAfford}
                    isBuying={buying === item.id}
                    onBuy={() => handleBuy(item)}
                    onPreview={() => setBundlePreview(item)}
                  />
                )
              }
              const isPremium = item.price.currency === 'stars'
              const canAfford = isPremium
                ? (user?.balance_stars ?? 0) >= item.price.amount
                : (user?.xgen_balance ?? 0) >= item.price.amount
              const isBuying = buying === item.id

              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 24 }}
                  className={`rounded-xl border p-3.5 space-y-2 ${
                    isPremium
                      ? 'bg-gradient-to-br from-amber-500/5 to-yellow-500/5 border-amber-500/15'
                      : 'bg-space-800/60 border-white/5'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      {item.icon_path ? (
                        <img src={item.icon_path} alt={item.name_key} className="shrink-0 w-10 h-10 rounded-lg object-cover" />
                      ) : (
                        <div className="shrink-0 w-10 h-10 rounded-lg border border-white/10 bg-black/30 flex items-center justify-center">
                          <ShoppingBag size={16} className="text-amber-500/70" />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <h3 className="font-display text-xs text-slate-200 uppercase tracking-wider truncate">
                          {item.name_key || 'Предмет'}
                        </h3>
                        <p className="text-[10px] text-slate-500 mt-1 leading-relaxed line-clamp-2">
                          {item.description_key || 'Описание отсутствует'}
                        </p>
                      </div>
                    </div>
                    <div className="shrink-0 text-right">
                      <span className={`font-display text-sm tabular-nums ${isPremium ? 'text-amber-400' : 'text-neon-cyan'}`}>
                        {item.price.amount}
                      </span>
                      <span className={`text-[10px] ml-0.5 ${isPremium ? 'text-amber-400' : 'text-neon-cyan'}`}>
                        {isPremium ? '⭐' : '✦'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleBuy(item)}
                      disabled={!canAfford || isBuying}
                      className={`flex-1 py-2 rounded-lg text-[10px] font-display uppercase tracking-wider transition-all ${
                        isBuying
                          ? 'bg-slate-700/50 text-slate-500'
                          : canAfford
                            ? isPremium
                              ? 'bg-gradient-to-r from-amber-500/20 to-yellow-500/20 text-amber-400 border border-amber-500/25 active:scale-[0.97]'
                              : 'bg-white/5 text-slate-300 border border-white/10 hover:bg-white/10 active:scale-[0.97]'
                            : 'bg-slate-800/50 text-slate-700 border border-slate-700/30 cursor-not-allowed'
                      }`}
                    >
                      {isBuying ? (
                        <span className="flex items-center justify-center gap-1">
                          <motion.span
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          >
                            <Package size={12} />
                          </motion.span>
                          Обрабатываем...
                        </span>
                      ) : canAfford ? (
                        'Приобрести'
                      ) : (
                        'Не хватает'
                      )}
                    </button>
                  </div>

                  {item.category === 'mystery' && (
                    <MysteryBoxPreview item={item} isAdmin={isAdmin} />
                  )}

                  <SellerComment item={item} visible={buyerCommentItem?.id === item.id} />
                </motion.div>
              )
            })
          ))}
        </motion.div>
      </AnimatePresence>

      <AnimatePresence>
        {successMsg && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="fixed left-4 right-4 bottom-20 z-[60] mx-auto max-w-lg"
          >
            <div className="bg-space-800/95 backdrop-blur-sm border border-amber-500/20 rounded-xl px-4 py-3 text-center shadow-[0_0_20px_rgba(245,158,11,.1)]">
              <p className="text-[11px] text-amber-400/90 font-display tracking-wider">
                ✔ {successMsg} — теперь ваш
              </p>
              <p className="text-[9px] text-slate-600 mt-1">
                «Спасибо за покупку. Возвращайтесь, когда нагуляете аппетит к сомнительным сделкам.»
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Reward reveal */}
      <AnimatePresence>
        {lastBuyResult && (
          <motion.div
            className="fixed inset-0 z-[70] flex items-end sm:items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={() => setLastBuyResult(null)} />
            <motion.div
              className="relative w-full sm:max-w-md bg-gradient-to-b from-space-800 to-space-900 border border-amber-500/20 rounded-t-2xl sm:rounded-2xl shadow-2xl overflow-hidden"
              initial={{ y: '100%', opacity: 0, scale: 0.9 }}
              animate={{ y: 0, opacity: 1, scale: 1 }}
              exit={{ y: '30%', opacity: 0, scale: 0.95 }}
              transition={{ type: 'spring', stiffness: 400, damping: 35, mass: 0.9 }}
            >
              <div className="px-5 pt-6 pb-2 text-center">
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20, delay: 0.1 }}
                  className="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-500/20 to-yellow-500/20 border border-amber-500/30 flex items-center justify-center mx-auto mb-3 overflow-hidden"
                >
                  {lastBuyResult.shopItem.bundle_image_url ? (
                    <img src={lastBuyResult.shopItem.bundle_image_url} alt="" className="w-full h-full object-cover" />
                  ) : lastBuyResult.shopItem.icon_path ? (
                    <img src={lastBuyResult.shopItem.icon_path} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <Gift size={24} className="text-amber-400" />
                  )}
                </motion.div>
                <h2 className="font-display text-sm text-amber-400 uppercase tracking-[0.15em]">
                  {lastBuyResult.shopItem.is_bundle
                    ? (lastBuyResult.shopItem.bundle_name || 'Набор')
                    : (lastBuyResult.shopItem.name_key || 'Покупка')}
                </h2>
                <p className="text-[10px] text-slate-500 mt-1">
                  «Вселенная щедра сегодня. Или просто издевается.»
                </p>
              </div>

              <div className="px-5 py-4 space-y-2">
                {lastBuyResult.shopItem.is_bundle
                  ? (lastBuyResult.shopItem.bundle_items_info || []).map((b, i) => (
                    <motion.div
                      key={b.item_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2 + i * 0.08 }}
                      className="flex items-center gap-3 bg-white/5 rounded-xl px-3.5 py-3 border border-white/5"
                    >
                      <div className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center overflow-hidden ${
                        b.type === 'artifact'
                          ? 'bg-purple-500/15 border border-purple-500/25'
                          : 'bg-neon-cyan/10 border border-neon-cyan/20'
                      }`}>
                        {b.image_url ? (
                          <img src={b.image_url} alt={b.name} className="w-full h-full object-cover" />
                        ) : b.type === 'artifact' ? (
                          <Diamond size={14} className="text-purple-400" />
                        ) : (
                          <Package size={14} className="text-neon-cyan" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-slate-200 truncate">{b.name}</p>
                        <p className="text-[9px] text-slate-500 mt-0.5">
                          {b.type === 'artifact' ? 'Артефакт' : 'Ресурс'}
                          {b.rarity ? ` · ${b.rarity}` : ''}
                        </p>
                      </div>
                      {b.quantity > 1 && (
                        <span className="shrink-0 text-xs text-slate-400 font-mono">×{b.quantity}</span>
                      )}
                    </motion.div>
                  ))
                  : lastBuyResult.response.granted.map((g, i) => {
                    const itemInfo = lastBuyResult.shopItem.bundle_items_info?.find(
                      (b) => b.item_id === g.item_config_id
                    )
                    const displayName = itemInfo?.name || g.name_key || 'Неизвестный предмет'
                    const displayQty = g.quantity || itemInfo?.quantity || 1
                    const displayImage = itemInfo?.image_url
                    const displayType = itemInfo?.type || g.type
                    const displayRarity = itemInfo?.rarity

                    return (
                      <motion.div
                        key={`${g.item_config_id}-${i}`}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 + i * 0.08 }}
                        className="flex items-center gap-3 bg-white/5 rounded-xl px-3.5 py-3 border border-white/5"
                      >
                        <div className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center overflow-hidden ${
                          displayType === 'artifact'
                            ? 'bg-purple-500/15 border border-purple-500/25'
                            : 'bg-neon-cyan/10 border border-neon-cyan/20'
                        }`}>
                          {displayImage ? (
                            <img src={displayImage} alt={displayName} className="w-full h-full object-cover" />
                          ) : displayType === 'artifact' ? (
                            <Diamond size={14} className="text-purple-400" />
                          ) : (
                            <Package size={14} className="text-neon-cyan" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-slate-200 truncate">
                            {displayName}
                          </p>
                          <p className="text-[9px] text-slate-500 mt-0.5">
                            {displayType === 'artifact' ? 'Артефакт' : 'Ресурс'}
                            {displayRarity ? ` · ${displayRarity}` : ''}
                            {g.tier ? ` · T${g.tier}` : ''}
                          </p>
                        </div>
                        {displayQty > 1 && (
                          <span className="shrink-0 text-xs text-slate-400 font-mono">
                            ×{displayQty}
                          </span>
                        )}
                      </motion.div>
                    )
                  })
                }
              </div>

              <div className="px-5 pb-6 pt-2">
                <button
                  onClick={() => setLastBuyResult(null)}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-amber-500/20 to-yellow-500/20 border border-amber-500/25 text-amber-400 text-[11px] font-display uppercase tracking-wider active:scale-[0.97] transition-all"
                >
                  Забрать
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      {/* Coin particles */}
      {coinParticles.map((p) => (
        <span
          key={p.id}
          className="animate-coin-fly"
          style={{
            left: p.x,
            top: p.y,
            '--dx': `${p.tx * 0.3}px`,
            '--dy': `${p.ty * 0.3}px`,
            '--tx': `${p.tx}px`,
            '--ty': `${p.ty}px`,
          } as React.CSSProperties}
        >
          {p.emoji}
        </span>
      ))}

      <ConfirmDialog
        open={!!starsConfirmItem}
        title="Купить за Stars?"
        description={`Потратить ${starsConfirmItem?.price.amount ?? 0} ⭐ на ${starsConfirmItem?.name_key ?? ''}? Stars списываются безвозвратно.`}
        confirmLabel={`Купить за ${starsConfirmItem?.price.amount ?? 0}⭐`}
        onConfirm={() => {
          if (starsConfirmItem) {
            executeBuy(starsConfirmItem)
            setStarsConfirmItem(null)
          }
        }}
        onCancel={() => setStarsConfirmItem(null)}
      />

      <ConfirmDialog
        open={!!xgenConfirmItem}
        title={xgenConfirmItem?.is_bundle ? `Купить «${xgenConfirmItem.bundle_name || 'Набор'}»?` : `Купить «${xgenConfirmItem?.name_key || 'Товар'}»?`}
        description={
          xgenConfirmItem?.is_bundle ? (
            <div className="space-y-2.5">
              {xgenConfirmItem.bundle_description && (
                <p className="text-slate-500 text-[10px] italic">{xgenConfirmItem.bundle_description}</p>
              )}
              <div className="space-y-1.5 max-h-[240px] overflow-y-auto">
                {(xgenConfirmItem.bundle_items_info || []).map((b) => (
                  <div key={b.item_id} className="flex items-center gap-2 bg-white/5 rounded-lg px-2.5 py-2">
                    <div className="shrink-0 w-6 h-6 rounded-md overflow-hidden bg-black/30 flex items-center justify-center">
                      {b.image_url ? (
                        <img src={b.image_url} alt={b.name} className="w-full h-full object-cover" />
                      ) : (
                        <Package size={12} className="text-slate-500" />
                      )}
                    </div>
                    <span className="flex-1 text-[11px] text-slate-300 truncate">{b.name}</span>
                    {b.quantity > 1 && (
                      <span className="shrink-0 text-[10px] text-amber-400 font-mono">×{b.quantity}</span>
                    )}
                  </div>
                ))}
              </div>
              <p className="text-slate-300 text-[11px] pt-1">
                Стоимость: <span className="text-neon-cyan font-mono">{xgenConfirmItem.price.amount} XGen</span>
              </p>
            </div>
          ) : (
            `${xgenConfirmItem?.name_key || 'Товар'} — ${xgenConfirmItem?.price.amount ?? 0} XGen.\nУ вас на счету: ${user?.xgen_balance ?? 0} XGen`
          )
        }
        confirmLabel="Купить"
        onConfirm={() => {
          if (xgenConfirmItem) {
            executeBuy(xgenConfirmItem)
            setXgenConfirmItem(null)
          }
        }}
        onCancel={() => setXgenConfirmItem(null)}
      />

      <BundlePreviewModal
        open={bundlePreview !== null}
        bundleName={bundlePreview?.bundle_name || bundlePreview?.name_key || '\u041d\u0430\u0431\u043e\u0440'}
        bundleDescription={bundlePreview?.bundle_description}
        items={bundlePreview?.bundle_items_info || []}
        onClose={() => setBundlePreview(null)}
      />
    </div>
    </PullToRefresh>
  )
}
