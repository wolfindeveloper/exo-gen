/**
 * Модальное окно детальной информации о зоне.
 * Полноэкранное с backdrop blur, анимацией появления.
 */

import { useState, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Shield, AlertTriangle, Sparkles, Rocket, Zap } from 'lucide-react'
import toast from 'react-hot-toast'
import { startExpedition } from '../../lib/api-helpers'
import { playSound } from '../../lib/sounds'
import { usePlayerStore, type PlayerShip } from '../../store/usePlayerStore'
import type { GalaxyZoneConfig } from '../../types'
import { useI18n } from '../../hooks/useI18n'

interface ZoneDetailModalProps {
  zone: GalaxyZoneConfig | null
  onClose: () => void
  language?: 'ru' | 'en' | 'la'
}

/** Получает локализованное значение */
function getLocalized(
  value: string | Record<string, string> | undefined,
  lang: string,
  fallback: string
): string {
  if (!value) return fallback
  if (typeof value === 'string') return value
  return value[lang] || value.en || value.ru || fallback
}

/** Цвет бейджа риска */
function getRiskBadgeColor(riskPct: number): string {
  if (riskPct < 30) return 'bg-green-500/20 text-green-400 border-green-500/30'
  if (riskPct < 60) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
  return 'bg-red-500/20 text-red-400 border-red-500/30'
}

/** Цвет градиента кнопки */
function getButtonGradient(isRisky: boolean): string {
  return isRisky
    ? 'from-red-500 to-purple-600'
    : 'from-neon-cyan to-purple-500'
}

/** Получает название корабля на нужном языке */
function getShipName(ship: PlayerShip, lang: string): string {
  const nameObj = ship.name as Record<string, string>
  return nameObj?.[lang] || nameObj?.en || nameObj?.ru || ship.slug
}

/** Рассчитывает модификатор риска на основе соотношения тиров */
function calculateRiskModifier(shipTier: number, zoneTier: number): {
  riskMultiplier: number
  label: string
  color: string
} {
  const diff = shipTier - zoneTier

  // Корабль ниже тира зоны → риск увеличивается
  if (diff < 0) {
    const multiplier = 1 + Math.abs(diff) * 0.25 // -1 тир = +25%, -2 = +50%
    return {
      riskMultiplier: multiplier,
      label: `+${Math.round((multiplier - 1) * 100)}%`,
      color: 'text-red-400',
    }
  }

  // Корабль выше тира зоны → риск уменьшается
  if (diff > 0) {
    const multiplier = 1 - diff * 0.15 // +1 тир = -15%, +2 = -30%
    return {
      riskMultiplier: Math.max(0.5, multiplier), // Минимум 50% риска
      label: `-${Math.round((1 - Math.max(0.5, multiplier)) * 100)}%`,
      color: 'text-green-400',
    }
  }

  // Тир совпадает
  return {
    riskMultiplier: 1,
    label: '—',
    color: 'text-gray-400',
  }
}

export function ZoneDetailModal({ zone, onClose, language = 'ru' }: ZoneDetailModalProps) {
  // ============================================================
  // ВСЕ ХУКИ ВЫЗЫВАЮТСЯ БЕЗУСЛОВНО — ДО ЛЮБОГО УСЛОВНОГО ВОЗВРАТА
  // ============================================================

  // 1. Zustand store
  const { player, getAvailableShips } = usePlayerStore()
  const { t } = useI18n()
  const availableShips = getAvailableShips()

  // 2. Local state
  const [selectedShip, setSelectedShip] = useState<PlayerShip | null>(null)
  const [selectedTier, setSelectedTier] = useState<number | null>(null)
  const [selectedMode, setSelectedMode] = useState<'stable' | 'push' | 'overdrive'>('stable')
  const [launching, setLaunching] = useState(false)

  // 3. useCallback
  const handleLaunch = useCallback(async () => {
    if (!zone || !selectedShip) return
    setLaunching(true)
    playSound('expedition')

    try {
      const fuelSlug = zone.tier === 1
        ? 'fuel_t1_mangan_hydride'
        : `fuel_t${zone.tier}_deuterium_x`

      await startExpedition(selectedShip.slug, zone.tier, fuelSlug, selectedMode)
      toast.success(t('zone.toast.launched'))
      playSound('success')
      onClose()
    } catch (err) {
      console.error('Expedition start failed:', err)
      toast.error(t('zone.toast.no.fuel'))
      playSound('error')
    } finally {
      setLaunching(false)
    }
  }, [zone, selectedShip, selectedMode, onClose])

  // 4. useMemo — total loot weight
  const totalLootWeight = useMemo(
    () => (zone?.loot_table || []).reduce((sum, i) => sum + i.weight, 0),
    [zone?.loot_table]
  )

  // 5. useMemo — repair drop weights
  const repairDropWeights = useMemo(() => {
    const weights = zone?.repair_drop_weights
    if (!weights) return []
    const total = Object.values(weights).reduce((s, v) => s + v, 0)
    return Object.entries(weights).map(([slug, weight]) => ({
      slug,
      tier: parseInt(slug.replace('repair_matter_t', ''), 10),
      chance: total > 0 ? ((weight / total) * 100).toFixed(0) : '0',
    }))
  }, [zone?.repair_drop_weights])

  // 5. useMemo — ships grouped by tier
  const shipsByTier = useMemo(() => {
    const grouped: Record<number, PlayerShip[]> = {}
    availableShips.forEach((ship) => {
      if (!grouped[ship.tier]) grouped[ship.tier] = []
      grouped[ship.tier].push(ship)
    })
    return grouped
  }, [availableShips])

  // ============================================================
  // УСЛОВНЫЙ ВОЗВРАТ — ТОЛЬКО ПОСЛЕ ВСЕХ ХУКОВ
  // ============================================================
  if (!zone) return null

  // ============================================================
  // ВЫЧИСЛЕНИЯ (не хуки — можно вызывать условно)
  // ============================================================
  const name = getLocalized(zone.name, language, zone.slug)
  const lore = getLocalized(zone.lore, language, '')
  const riskPct = zone.risk_pct ?? 0
  const rareChance = zone.rare_chance ?? 0
  const lootTable = zone.loot_table || []
  const dropTable = zone.drop_table || []

  const filteredShips = selectedTier
    ? availableShips.filter((s) => s.tier === selectedTier)
    : availableShips

  const riskModifier = selectedShip
    ? calculateRiskModifier(selectedShip.tier, zone.tier)
    : null

  const adjustedRisk = riskModifier
    ? Math.round(riskPct * riskModifier.riskMultiplier)
    : riskPct

  const isRisky = (selectedShip?.tier || 0) < zone.tier
  const buttonGradient = getButtonGradient(isRisky)
  const buttonText = !selectedShip
    ? t('zone.detail.select.ship')
    : isRisky
    ? `${t('zone.detail.try.luck')} (${getShipName(selectedShip, language)})`
    : `${t('zone.detail.explore')}: ${name}`

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[70] flex items-center justify-center p-3"
        onClick={onClose}
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/80 backdrop-blur-md" />

        {/* Modal content */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="relative w-full max-w-lg max-h-[85vh] bg-cosmic-bg border border-cosmic-border rounded-3xl overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="relative px-5 pt-5 pb-3 border-b border-cosmic-border">
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-xl hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>

            <div className="flex items-center gap-3">
              <h2 className="text-lg font-bold bg-gradient-to-r from-neon-cyan to-purple-400 bg-clip-text text-transparent">
                {name}
              </h2>
            </div>

            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs px-2 py-0.5 rounded-full bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30 font-medium">
                {t('misc.tier')} {zone.tier}
              </span>
              <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${getRiskBadgeColor(adjustedRisk)}`}>
                {adjustedRisk > 50 ? <AlertTriangle className="w-3 h-3 inline mr-1" /> : <Shield className="w-3 h-3 inline mr-1" />}
                {t('zone.detail.risk')}: {adjustedRisk}%
              </span>
              {rareChance > 0 && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30 font-medium">
                  <Sparkles className="w-3 h-3 inline mr-1" />
                  {t('zone.detail.rare')}: {rareChance}%
                </span>
              )}
            </div>
          </div>

          {/* Scrollable content */}
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
            {/* Art placeholder */}
            <div className="relative w-full aspect-video rounded-xl overflow-hidden bg-cosmic-bg border border-cosmic-border">
              <img
                src={`https://picsum.photos/seed/${zone.slug}/600/400`}
                alt={name}
                className="w-full h-full object-cover opacity-60"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-cosmic-bg via-transparent to-transparent" />
            </div>

            {/* Lore */}
            {lore && (
              <div>
                <h3 className="text-sm font-bold text-white mb-2">{t('zone.detail.lore')}</h3>
                <p className="text-sm text-gray-300 leading-relaxed">{lore}</p>
              </div>
            )}

            {/* Loot Table */}
            <div>
              <h3 className="text-sm font-bold text-white mb-2">{t('zone.detail.loot')}</h3>
              <div className="space-y-1.5">
                {lootTable.length > 0 ? (
                  lootTable.map((item) => {
                    const chance = totalLootWeight > 0
                      ? ((item.weight / totalLootWeight) * 100).toFixed(0)
                      : '0'
                    return (
                      <div
                        key={item.essence_slug}
                        className="flex items-center justify-between px-3 py-2 rounded-lg bg-white/5 border border-white/10"
                      >
                        <span className="text-xs text-gray-300">{item.essence_slug}</span>
                        <span className="text-xs font-bold text-neon-cyan">{chance}%</span>
                      </div>
                    )
                  })
                ) : (
                  dropTable.map((item) => (
                    <div
                      key={item}
                      className="flex items-center justify-between px-3 py-2 rounded-lg bg-white/5 border border-white/10"
                    >
                      <span className="text-xs text-gray-300">{item}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Repair Mat Drops */}
            {repairDropWeights.length > 0 && (
              <div>
                <h3 className="text-sm font-bold text-white mb-2">
                  🔧 {t('zone.detail.repair')}
                </h3>
                <p className="text-[10px] text-gray-500 mb-2">
                  {t('zone.detail.repair.hint')}
                </p>
                <div className="space-y-1.5">
                  {repairDropWeights.map((mat) => (
                    <div
                      key={mat.slug}
                      className="flex items-center justify-between px-3 py-2 rounded-lg bg-white/5 border border-white/10"
                    >
                      <span className="text-xs text-gray-300">
                        {t('zone.detail.repair.kit')} T{mat.tier}
                      </span>
                      <span className="text-xs font-bold text-yellow-400">
                        {mat.chance}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Risk Analysis */}
            <div>
              <h3 className="text-sm font-bold text-white mb-2">{t('zone.detail.risk.analysis')}</h3>
              <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">{t('zone.detail.risk.base')}</span>
                  <span className="text-sm font-bold text-gray-300">{riskPct}%</span>
                </div>
                {riskModifier && (
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">{t('zone.detail.risk.modifier')}</span>
                    <span className={`text-sm font-bold ${riskModifier.color}`}>
                      {riskModifier.label}
                    </span>
                  </div>
                )}
                <div className="flex items-center justify-between pt-1 border-t border-white/10">
                  <span className="text-xs text-gray-400">{t('zone.detail.risk.final')}</span>
                  <span className={`text-sm font-bold ${adjustedRisk > 60 ? 'text-red-400' : adjustedRisk > 30 ? 'text-yellow-400' : 'text-green-400'}`}>
                    {adjustedRisk}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">{t('zone.detail.risk.damage')}</span>
                  <span className="text-sm font-bold text-orange-400">
                    {Math.round(adjustedRisk * 0.6)}%
                  </span>
                </div>
                {adjustedRisk > 50 && (
                  <div className="flex items-center gap-2 pt-1 border-t border-white/10">
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                    <span className="text-xs text-red-400">{t('zone.detail.risk.high')} T{zone.tier}+</span>
                  </div>
                )}
              </div>
            </div>

            {/* Ship Selection */}
            <div>
              <h3 className="text-sm font-bold text-white mb-2">{t('zone.detail.ship.select')}</h3>

              {/* Кнопки тиров */}
              <div className="flex gap-2 mb-3">
                {[1, 2, 3, 4, 5].map((tier) => {
                  const hasShips = (shipsByTier[tier]?.length || 0) > 0
                  const isSelected = selectedTier === tier
                  return (
                    <button
                      key={tier}
                      disabled={!hasShips}
                      onClick={() => setSelectedTier(isSelected ? null : tier)}
                      className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
                        isSelected
                          ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50'
                          : hasShips
                          ? 'bg-white/5 text-gray-400 border border-white/10 hover:border-white/20'
                          : 'bg-white/5 text-gray-600 border border-white/10 cursor-not-allowed opacity-50'
                      }`}
                    >
                      T{tier}
                    </button>
                  )
                })}
              </div>

              {/* Список кораблей */}
              <div className="space-y-2">
                {filteredShips.length === 0 ? (
                    <p className="text-xs text-gray-500 text-center py-4">
                      {t('zone.detail.ship.empty')}
                    </p>
                ) : (
                  filteredShips.map((ship) => {
                    const isSelected = selectedShip?.id === ship.id
                    const isLowerTier = ship.tier < zone.tier
                    const isHigherTier = ship.tier > zone.tier

                    return (
                      <motion.button
                        key={ship.id}
                        onClick={() => {
                          setSelectedShip(isSelected ? null : ship)
                        }}
                        whileTap={{ scale: 0.98 }}
                        className={`w-full px-4 py-3 rounded-xl border text-left transition-all ${
                          isSelected
                            ? 'bg-neon-cyan/10 border-neon-cyan/50 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                            : 'bg-white/5 border-white/10 hover:border-white/20'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg ${
                              ship.tier <= 2 ? 'bg-gray-500/10' :
                              ship.tier === 3 ? 'bg-blue-500/10' :
                              ship.tier === 4 ? 'bg-purple-500/10' : 'bg-yellow-500/10'
                            }`}>
                              {ship.tier <= 2 ? '🚀' : ship.tier === 3 ? '🛸' : ship.tier === 4 ? '🔥' : '⭐'}
                            </div>
                            <div>
                              <p className="text-sm font-bold text-white">
                                {getShipName(ship, language)}
                              </p>
                              <p className="text-[10px] text-gray-400">
                                T{ship.tier} · {t('zone.detail.ship.stability')}: {ship.stability}%
                              </p>
                            </div>
                          </div>

                          {/* Индикатор соотношения тиров */}
                          {isLowerTier && (
                              <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
                                ⚠️ {t('zone.detail.ship.danger')}
                              </span>
                          )}
                          {isHigherTier && (
                              <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-500/20 text-green-400 border border-green-500/30">
                                ✓ {t('zone.detail.ship.safe')}
                              </span>
                          )}
                          {!isLowerTier && !isHigherTier && (
                              <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-500/20 text-gray-400 border border-gray-500/30">
                                {t('zone.detail.ship.equal')}
                              </span>
                          )}
                        </div>
                      </motion.button>
                    )
                  })
                )}
              </div>

              {/* Warning if selected ship tier < zone tier */}
              {selectedShip && selectedShip.tier < zone.tier && (
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 mt-3 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20"
                >
                  <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
                    <span className="text-xs text-red-400">
                      ⚠️ {t('zone.detail.ship.warning')}
                    </span>
                </motion.div>
              )}

              {/* Info if selected ship tier > zone tier */}
              {selectedShip && selectedShip.tier > zone.tier && (
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 mt-3 px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/20"
                >
                  <Shield className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span className="text-xs text-green-400">
                      ✓ {t('zone.detail.ship.info')}
                    </span>
                </motion.div>
              )}
            </div>
          </div>

          {/* Action area */}
          <div className="px-5 py-4 border-t border-cosmic-border space-y-3">
            {/* Overdrive Mode Selector */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-3.5 h-3.5 text-yellow-400" />
                <span className="text-xs font-bold text-gray-300">{t('overdrive.title')}</span>
              </div>
              <div className="flex gap-1.5">
                {([
                  { mode: 'stable' as const, icon: '🛡️', label: t('overdrive.stable'), desc: t('overdrive.stable.desc'), cost: t('overdrive.stable.cost'), costColor: 'text-green-400' },
                  { mode: 'push' as const, icon: '⚡', label: t('overdrive.push'), desc: t('overdrive.push.desc'), cost: t('overdrive.push.cost'), costColor: 'text-yellow-400' },
                  { mode: 'overdrive' as const, icon: '🔥', label: t('overdrive.overdrive'), desc: t('overdrive.overdrive.desc'), cost: t('overdrive.overdrive.cost'), costColor: 'text-red-400' },
                ]).map(({ mode, icon, label, desc, cost, costColor }) => {
                  const isSelected = selectedMode === mode
                  return (
                    <button
                      key={mode}
                      onClick={() => setSelectedMode(mode)}
                      className={`flex-1 px-2 py-2 rounded-xl border text-left transition-all ${
                        isSelected
                          ? mode === 'stable'
                            ? 'border-green-500/50 bg-green-500/10'
                            : mode === 'push'
                            ? 'border-yellow-500/50 bg-yellow-500/10'
                            : 'border-red-500/50 bg-red-500/10'
                          : 'border-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="text-sm">{icon}</div>
                      <p className={`text-[10px] font-bold mt-0.5 ${isSelected ? 'text-white' : 'text-gray-400'}`}>{label}</p>
                      <p className="text-[8px] text-gray-500 leading-tight">{desc}</p>
                      <p className={`text-[9px] font-bold mt-1 ${costColor}`}>{cost}</p>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Launch button */}
            <motion.button
              onClick={handleLaunch}
              disabled={launching || !selectedShip}
              className={`relative w-full min-h-[44px] rounded-xl font-bold text-white text-sm overflow-hidden disabled:opacity-50`}
              whileTap={{ scale: 0.98 }}
            >
              <div className={`absolute inset-0 bg-gradient-to-r ${buttonGradient}`} />
              {launching && (
                <motion.div
                  className="absolute inset-0 bg-white/20"
                  animate={{ opacity: [0, 0.3, 0] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              )}
              <span className="relative flex items-center justify-center gap-2">
                <Rocket className="w-4 h-4" />
                {launching ? t('zone.detail.launching') : buttonText}
              </span>
            </motion.button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
