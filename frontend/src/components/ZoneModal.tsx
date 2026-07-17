import { useEffect, useMemo, useState } from 'react'
import { motion } from 'motion/react'

import { calculateZoneStats } from '../lib/expeditionCalc'
import { statLabels } from '../lib/stats'
import { canAccessZone, formatUnlockHint } from '../lib/progression'
import { useGameStore } from '../store/game'
import type { Zone } from '../types'

const DROP_TYPE_CONFIG: Record<string, { label: string; emoji: string; color: string; bg: string; border: string }> = {
  xgen: { label: 'XGen', emoji: '💎', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30' },
  fragments: { label: 'Фрагменты', emoji: '📜', color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/30' },
  item: { label: 'Предмет', emoji: '📦', color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/30' },
}

const RARITY_CONFIG: Record<string, { label: string; color: string; glow: string }> = {
  common: { label: 'Обычный', color: '#94a3b8', glow: 'rgba(148,163,184,0.3)' },
  uncommon: { label: 'Необычный', color: '#22c55e', glow: 'rgba(34,197,94,0.3)' },
  rare: { label: 'Редкий', color: '#3b82f6', glow: 'rgba(59,130,246,0.3)' },
  epic: { label: 'Эпический', color: '#a855f7', glow: 'rgba(168,85,247,0.3)' },
  legendary: { label: 'Легендарный', color: '#f59e0b', glow: 'rgba(245,158,11,0.4)' },
}

function getChanceBadgeStyle(chance: number) {
  const pct = Math.round(chance * 100)
  if (pct >= 80) return { color: '#22c55e', label: 'Часто', bg: 'bg-green-500/10', border: 'border-green-500/30' }
  if (pct >= 40) return { color: '#eab308', label: 'Средне', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' }
  if (pct >= 15) return { color: '#f97316', label: 'Редко', bg: 'bg-orange-500/10', border: 'border-orange-500/30' }
  return { color: '#ef4444', label: 'Очень редко', bg: 'bg-red-500/10', border: 'border-red-500/30' }
}

const zoneEmoji: Record<string, string> = {
  the_outskirts_of_sanity: '🌌',
  scrap_yard: '🗑️',
  nebula_warm_tea: '🍵',
  the_belt_of_statistical_errors: '☄️',
  the_edge_of_nowhere_filling_station: '⛽',
  the_syntax_error_nebula: '💻',
  the_lost_sock_archipelago: '🧦',
  the_terminal_of_eternal_queue: '⌛',
  the_zone_of_mild_inconvenience: '😤',
  the_planet_echo_monday: '📅',
  'the_credit-score_black_hole': '💳',
  "the_schrödinger's_sector": '📦',
  the_archive_of_all_mistakes: '📚',
  the_nebula_of_twisted_recalls: '🌀',
  the_zero_meridian_of_absurdity: '⏳',
  the_zenith_of_status: '👑',
  the_sector_of_singularity_architects: '🏛️',
  the_library_of_great_deals: '📖',
  the_cloud_of_pure_ether: '☁️',
  'the_planet_of_ego-olympus': '🏔️',
  the_administrative_singularity: '🗑️',
  the_boardroom_of_creation: '🪑',
  the_nebula_of_random_epiphany: '💡',
  the_planet_of_placebo_effect: '💊',
  the_end_of_shift_station: '🌆',
}

interface ZoneModalProps {
  zone: Zone
  onClose: () => void
  onStart: () => void
  isLoading: boolean
  playerLevel?: number
}

export function ZoneModal({ zone, onClose, onStart, isLoading, playerLevel = 1 }: ZoneModalProps) {
  const ships = useGameStore((s) => s.ships)
  const loadShips = useGameStore((s) => s.loadShips)
  const [confirming, setConfirming] = useState(false)
  const [imgError, setImgError] = useState(false)

  const zoneTier = zone.tier ?? 1
  const unlockStatus = canAccessZone(playerLevel, zoneTier)
  const isLocked = !unlockStatus.isUnlocked

  useEffect(() => {
    if (ships.length === 0) loadShips()
  }, [])

  const mainShip = ships[0] ?? null
  const speedMod = mainShip?.speed ?? 1.0
  const luck = mainShip?.luck ?? 0
  const artifactsContent = useGameStore((s) => s.artifactsContent)
  const resourcesContent = useGameStore((s) => s.resourcesContent)
  const inventory = useGameStore((s) => s.inventory)

  const itemInfoMap = useMemo(() => {
    const map = new Map<string, { name: string; icon: string; rarity: string; type: string; description?: string }>()
    for (const a of artifactsContent) {
      map.set(a.id, {
        name: a.name_key,
        icon: a.icon_path || '⚙',
        rarity: a.rarity || 'common',
        type: 'artifact',
        description: a.description_key,
      })
    }
    for (const r of resourcesContent) {
      map.set(r.id, {
        name: r.name_key,
        icon: r.icon_path || (r.resource_type === 'fuel' ? '⛽' : '🔧'),
        rarity: 'common',
        type: 'resource',
        description: r.description_key,
      })
    }
    for (const inv of inventory) {
      if (!map.has(inv.item.id)) {
        map.set(inv.item.id, {
          name: inv.item.name,
          icon: inv.item.image_url || '📦',
          rarity: inv.item.rarity || 'common',
          type: inv.item.type,
          description: inv.item.description,
        })
      }
    }
    return map
  }, [artifactsContent, resourcesContent, inventory])

  const totalDefense = useMemo(() => {
    const baseDefense = mainShip?.defense ?? 0
    const equippedIds = mainShip?.equipment?.artifacts?.map(a => a.id) ?? []
    const artifactDefense = artifactsContent
      .filter(a => equippedIds.includes(a.id))
      .reduce((sum, a) => sum + (a.stats_modifiers?.defense ?? 0), 0)
    return baseDefense + artifactDefense
  }, [mainShip, artifactsContent])

  const artifactBonuses = useMemo(() => {
    const mods: Record<string, number> = {}
    if (luck) mods.speed_mod = luck
    if (totalDefense > 0) mods.damage_reduction = totalDefense
    return Object.keys(mods).length > 0 ? [mods] : []
  }, [luck, totalDefense])

  const calcedStats = useMemo(() => {
    if (!mainShip) return null
    return calculateZoneStats(
      zone.optimism_risk,
      zone.fuel_cost,
      zone.duration_seconds / 3600,
      mainShip.optimism,
      speedMod,
      mainShip.tea_level,
      artifactBonuses,
    )
  }, [mainShip, speedMod, zone, artifactBonuses])

  const canLaunch = !!mainShip && !!calcedStats?.fuelOk

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <motion.div
        className="relative w-full sm:max-w-md max-h-[90vh] overflow-y-auto bg-space-900 border border-white/10 rounded-t-2xl sm:rounded-2xl shadow-2xl"
        initial={{ y: '100%', opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: '30%', opacity: 0 }}
        transition={{ type: 'spring', stiffness: 400, damping: 35, mass: 0.9 }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 z-10 w-8 h-8 rounded-full bg-black/40 backdrop-blur flex items-center justify-center text-white/70 hover:text-white transition-colors"
        >
          ✕
        </button>

        <div className={`relative aspect-[3/2] ${zone.image_url && !imgError ? '' : 'bg-gradient-to-br from-neon-cyan/30 via-space-800 to-space-950'} overflow-hidden`}>
          {zone.image_url && !imgError ? (
            <img
              src={zone.image_url}
              alt={zone.name}
              className="w-full h-full object-cover"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className={'w-full h-full bg-gradient-to-br from-neon-cyan/30 via-space-800 to-space-950 flex items-center justify-center'}>
              <div className="text-center">
                <motion.div
                  className="text-5xl mb-1"
                  initial={{ scale: 0, rotate: -20 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                >
                  {zoneEmoji[zone.id] || '🌌'}
                </motion.div>
                <h2 className="font-display text-sm uppercase tracking-[0.15em] text-neon-cyan">{zone.name}</h2>
                <span className="text-[10px] text-white/40 font-display uppercase tracking-wider mt-0.5 block">Tier {zone.tier ?? 1}</span>
              </div>
            </div>
          )}
          {zone.image_url && !imgError && (
            <>
              <div className="absolute inset-0 bg-gradient-to-t from-space-900/80 via-transparent to-transparent" />
              <div className="absolute bottom-3 left-5">
                <h2 className="font-display text-sm uppercase tracking-[0.15em] drop-shadow-lg text-neon-cyan">{zone.name}</h2>
                <span className="text-[10px] text-white/50 font-display uppercase tracking-wider mt-0.5 block drop-shadow">Tier {zone.tier ?? 1}</span>
              </div>
            </>
          )}
        </div>

        <div className="p-5 space-y-5 pb-24">
          <p className="text-xs text-slate-400 leading-relaxed">{zone.description}</p>

          <div>
            <h4 className="text-[10px] font-display uppercase tracking-wider text-slate-500 mb-2">Характеристики</h4>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: '⛽ Топливо', base: zone.fuel_cost, calc: calcedStats?.effectiveFuelCost },
                { label: '⏱ Время', base: `${Math.round(zone.duration_seconds / 3600)}ч`, calc: calcedStats ? `${calcedStats.durationHours}ч` : null },
                { label: '⚠ Риск зоны', base: `${Math.round(zone.optimism_risk * 100)}%`, calc: null },
              ].map((item) => (
                <div key={item.label} className="glass-card p-3 text-center">
                  <p className="text-[10px] text-slate-500 mb-1">{item.label}</p>
                  <p className="text-sm font-display text-slate-300">{item.base}</p>
                  {item.calc && (
                    <p className="text-[10px] mt-0.5 font-display text-neon-cyan">
                      {item.calc}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {calcedStats && (
            <div className="space-y-2">
              {totalDefense > 0 && (
                <div className="flex justify-between text-xs bg-neon-green/5 border border-neon-green/20 rounded-lg px-3 py-2">
                  <span className="text-neon-green">🛡️ Защита корабля</span>
                  <span className="font-display text-neon-green tabular-nums">
                    -{Math.round(totalDefense * 100)}% урона
                  </span>
                </div>
              )}
              <div className="flex justify-between text-xs bg-space-600/30 rounded-lg px-3 py-2">
                <span className="text-slate-500">
                  💥 Потеря прочности
                  <span className="text-[9px] text-slate-600 ml-1">(от текущей)</span>
                </span>
                <span className="font-display text-neon-red tabular-nums">
                  -{calcedStats.estimatedMaxDamage}%
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">⚠ Эффективный риск</span>
                <span className="font-display text-slate-400 tabular-nums">
                  {calcedStats.riskPercent}%
                </span>
              </div>
            </div>
          )}

          {artifactBonuses.length > 0 && (
            <div>
              <h4 className="text-[10px] font-display uppercase tracking-wider text-slate-500 mb-2">Бонусы артефактов</h4>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(artifactBonuses[0]).map(([key, val]) => {
                  const color =
                    key === 'speed_mod' ? 'text-neon-cyan border-neon-cyan/20 bg-neon-cyan/10'
                    : key === 'damage_reduction' ? 'text-neon-green border-neon-green/20 bg-neon-green/10'
                    : key === 'fuel_efficiency' ? 'text-neon-amber border-neon-amber/20 bg-neon-amber/10'
                    : 'text-slate-400 border-white/10 bg-white/5'
                  return (
                    <span key={key} className={`text-[10px] px-2 py-1 rounded-md border ${color}`}>
                      {statLabels[key] || key} {val > 0 ? '+' : ''}{val}
                    </span>
                  )
                })}
              </div>
            </div>
          )}

          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-[10px] font-display uppercase tracking-wider text-slate-500">
                Возможная добыча
              </h4>
              <span className="text-[9px] text-slate-600 font-mono">
                {zone.loot_table.length} {zone.loot_table.length === 1 ? 'предмет' : 'предметов'}
              </span>
            </div>
            <div className="space-y-1.5">
              {zone.loot_table.map((loot, idx) => {
                const dropConfig = DROP_TYPE_CONFIG[loot.item_type] || DROP_TYPE_CONFIG.item
                const itemInfo = loot.item_id ? itemInfoMap.get(loot.item_id) : null
                const rarityInfo = itemInfo?.rarity ? RARITY_CONFIG[itemInfo.rarity] : RARITY_CONFIG.common
                const chanceStyle = getChanceBadgeStyle(loot.chance)
                const pct = Math.round(loot.chance * 100)
                const isGuaranteed = loot.chance >= 1.0
                return (
                  <motion.div
                    key={loot.item_id ?? idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex items-center gap-3 bg-space-700/30 border border-white/5 rounded-xl p-2.5 hover:bg-space-700/50 transition-colors"
                  >
                    <div
                      className="shrink-0 w-10 h-10 rounded-lg flex items-center justify-center overflow-hidden"
                      style={{
                        background: itemInfo?.type === 'artifact'
                          ? `radial-gradient(circle, ${rarityInfo.glow}, transparent 70%), rgba(15,20,32,0.6)`
                          : dropConfig.bg,
                        border: `1px solid ${itemInfo?.type === 'artifact' ? rarityInfo.color + '44' : dropConfig.border}`,
                        boxShadow: itemInfo?.type === 'artifact' ? `0 0 12px ${rarityInfo.glow}` : undefined,
                      }}
                    >
                      {itemInfo?.icon && (itemInfo.icon.startsWith('http') || itemInfo.icon.startsWith('/')) ? (
                        <img src={itemInfo.icon} alt="" className="w-full h-full object-cover" />
                      ) : (
                        <span className="text-lg">
                          {(itemInfo?.icon && itemInfo.icon.length > 2) ? '📦' : (itemInfo?.icon || dropConfig.emoji)}
                        </span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-0.5">
                        <span className="text-xs text-slate-200 font-medium truncate">
                          {itemInfo?.name || loot.item_name || dropConfig.label}
                        </span>
                        {loot.amount > 1 && (
                          <span className="shrink-0 text-[9px] font-mono text-slate-400 bg-white/5 px-1.5 py-0.5 rounded">
                            ×{loot.amount}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-1.5">
                        {itemInfo?.type === 'artifact' ? (
                          <span
                            className="text-[8px] font-display uppercase tracking-wider px-1.5 py-0.5 rounded border"
                            style={{
                              color: rarityInfo.color,
                              borderColor: `${rarityInfo.color}44`,
                              backgroundColor: `${rarityInfo.color}15`,
                            }}
                          >
                            {rarityInfo.label}
                          </span>
                        ) : (
                          <span className={`text-[8px] font-display uppercase tracking-wider px-1.5 py-0.5 rounded border ${dropConfig.color} ${dropConfig.border} ${dropConfig.bg}`}>
                            {dropConfig.label}
                          </span>
                        )}
                        {isGuaranteed && (
                          <span className="text-[8px] font-display uppercase tracking-wider px-1.5 py-0.5 rounded border text-green-400 border-green-500/30 bg-green-500/10">
                            ✓ Гарантировано
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="shrink-0 w-16 text-right">
                      <div className="flex items-center justify-end gap-1 mb-0.5">
                        <span className="text-sm font-mono font-bold tabular-nums" style={{ color: chanceStyle.color }}>
                          {pct}%
                        </span>
                      </div>
                      <div className="h-1 bg-space-900/50 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full rounded-full"
                          style={{ backgroundColor: chanceStyle.color }}
                          initial={{ width: 0 }}
                          animate={{ width: `${pct}%` }}
                          transition={{ duration: 0.8, delay: idx * 0.05, ease: 'easeOut' }}
                        />
                      </div>
                      <span className="text-[7px] uppercase tracking-wider block mt-0.5 text-right" style={{ color: chanceStyle.color }}>
                        {chanceStyle.label}
                      </span>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </div>

          {!mainShip && (
            <p className="text-xs text-neon-amber/70 text-center">Нет корабля</p>
          )}
          {mainShip && calcedStats && !calcedStats.fuelOk && (
            <p className="text-xs text-neon-red text-center">Недостаточно ⛽ для запуска</p>
          )}

          {isLocked ? (
            <div className="glass-card p-4 text-center border-amber-500/20 bg-amber-500/5">
              <div className="text-2xl mb-2">🔒</div>
              <p className="text-xs font-display uppercase tracking-wider text-amber-400 mb-1">
                Зона недоступна
              </p>
              <p className="text-[10px] text-slate-400">
                Требуется уровень <span className="text-amber-300 font-mono">{unlockStatus.requiredLevel}</span>
              </p>
              <p className="text-[9px] text-slate-600 mt-1">
                {formatUnlockHint(unlockStatus.requiredLevel!, playerLevel)}
              </p>
            </div>
          ) : confirming && canLaunch ? (
            <div className="flex gap-2">
              <button
                onClick={() => setConfirming(false)}
                className="flex-1 py-3.5 rounded-xl font-display text-sm uppercase tracking-wider transition border border-white/10 text-slate-400 hover:bg-space-700/50"
              >
                ← Отмена
              </button>
              <button
                disabled={isLoading}
                onClick={onStart}
                className="flex-[2] py-3.5 rounded-xl font-display text-sm uppercase tracking-wider transition disabled:opacity-30 bg-gradient-to-r from-neon-purple/80 to-neon-cyan/80 hover:from-neon-purple hover:to-neon-cyan"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <motion.span animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>◌</motion.span>
                    Старт...
                  </span>
                ) : (
                  '🚀 Точно запустить'
                )}
              </button>
            </div>
          ) : (
            <button
              disabled={!canLaunch || isLoading}
              onClick={() => setConfirming(true)}
              className="btn-glow w-full py-3.5 rounded-xl font-display text-sm uppercase tracking-wider transition disabled:opacity-30 bg-gradient-to-r from-neon-purple/80 to-neon-cyan/80 hover:from-neon-purple hover:to-neon-cyan"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <motion.span animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>◌</motion.span>
                  Старт...
                </span>
              ) : !calcedStats ? (
                'Загрузка...'
              ) : !calcedStats.fuelOk ? (
                'Недостаточно ⛽'
              ) : (
                '🚀 Запуск'
              )}
            </button>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}
