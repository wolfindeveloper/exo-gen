import { useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { ChevronDown, ChevronUp, FlaskConical, Gift } from 'lucide-react'

import type { ShopItem, LootBoxSimResult } from '../types'
import { api } from '../api/client'

const DROP_TYPE_CONFIG: Record<string, { label: string; emoji: string; color: string; bg: string; border: string }> = {
  xgen: { label: 'XGen', emoji: '💎', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30' },
  fragments: { label: 'Фрагменты', emoji: '📜', color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/30' },
  artifact: { label: 'Артефакт', emoji: '✨', color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/30' },
  item: { label: 'Предмет', emoji: '📦', color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/30' },
}

const RARITY_CONFIG: Record<string, { label: string; color: string; glow: string }> = {
  common: { label: 'Обычный', color: '#94a3b8', glow: 'rgba(148,163,184,0.3)' },
  uncommon: { label: 'Необычный', color: '#22c55e', glow: 'rgba(34,197,94,0.3)' },
  rare: { label: 'Редкий', color: '#3b82f6', glow: 'rgba(59,130,246,0.3)' },
  epic: { label: 'Эпический', color: '#a855f7', glow: 'rgba(168,85,247,0.3)' },
  legendary: { label: 'Легендарный', color: '#f59e0b', glow: 'rgba(245,158,11,0.4)' },
}

function getChanceBadgeStyle(chancePct: number) {
  if (chancePct >= 50) return { color: '#22c55e', label: 'Часто', bg: 'bg-green-500/10', border: 'border-green-500/30' }
  if (chancePct >= 20) return { color: '#eab308', label: 'Средне', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' }
  if (chancePct >= 5) return { color: '#f97316', label: 'Редко', bg: 'bg-orange-500/10', border: 'border-orange-500/30' }
  return { color: '#ef4444', label: 'Очень редко', bg: 'bg-red-500/10', border: 'border-red-500/30' }
}

interface MysteryBoxPreviewProps {
  item: ShopItem
  isAdmin: boolean
}

export function MysteryBoxPreview({ item, isAdmin }: MysteryBoxPreviewProps) {
  const [expanded, setExpanded] = useState(false)
  const [simulating, setSimulating] = useState(false)
  const [simResults, setSimResults] = useState<LootBoxSimResult[] | null>(null)
  const [simError, setSimError] = useState<string | null>(null)

  const rewards = item.rewards ?? []
  if (rewards.length === 0) return null

  const probabilistic = rewards.length > 0 ? rewards : []

  const chancePct = probabilistic.length > 0 ? Math.round(100 / probabilistic.length) : 0

  const handleSimulate = async () => {
    setSimulating(true)
    setSimError(null)
    try {
      const results = await api.simulateLootBox(item.id, 100)
      setSimResults(results)
    } catch (e) {
      setSimError((e as Error).message || 'Ошибка симуляции')
    } finally {
      setSimulating(false)
    }
  }

  return (
    <div className="mt-2 border-t border-white/5 pt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 w-full text-left group"
      >
        <Gift size={12} className="text-amber-400/60 shrink-0" />
        <span className="text-[10px] font-display uppercase tracking-wider text-amber-400/60 group-hover:text-amber-400/80 transition-colors">
          Что внутри?
        </span>
        <span className="text-[9px] text-slate-600 ml-auto mr-1">
          {rewards.length} {rewards.length === 1 ? 'награда' : 'наград'}
        </span>
        {expanded ? (
          <ChevronUp size={12} className="text-slate-600 shrink-0" />
        ) : (
          <ChevronDown size={12} className="text-slate-600 shrink-0" />
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="pt-2 space-y-1.5">
              {probabilistic.map((reward, idx) => {
                const typeKey = reward.type === 'artifact' ? 'artifact' : reward.type === 'xgen' ? 'xgen' : reward.type === 'fragments' ? 'fragments' : 'item'
                const dropConfig = DROP_TYPE_CONFIG[typeKey] ?? DROP_TYPE_CONFIG.item
                const isGuaranteed = reward.quantity === 1 && reward.type === 'item'
                const style = getChanceBadgeStyle(chancePct)

                let rarityInfo = RARITY_CONFIG.common
                if (reward.tier) {
                  const rarityByTier: Record<number, string> = { 1: 'common', 2: 'uncommon', 3: 'rare', 4: 'epic', 5: 'legendary' }
                  const rKey = rarityByTier[reward.tier] ?? 'common'
                  rarityInfo = RARITY_CONFIG[rKey]
                }

                return (
                  <motion.div
                    key={`${reward.item_config_id ?? reward.type}-${idx}`}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.04 }}
                    className={`flex items-center gap-2.5 rounded-lg p-2 border ${
                      isGuaranteed
                        ? 'border-green-500/30 bg-green-500/5'
                        : 'border-white/5 bg-space-700/30'
                    }`}
                  >
                    <div
                      className="shrink-0 w-8 h-8 rounded-md flex items-center justify-center"
                      style={{
                        background: reward.type === 'artifact'
                          ? `radial-gradient(circle, ${rarityInfo.glow}, transparent 70%), rgba(15,20,32,0.6)`
                          : undefined,
                        border: reward.type === 'artifact'
                          ? `1px solid ${rarityInfo.color}44`
                          : undefined,
                      }}
                    >
                      <span className="text-sm">
                        {reward.type === 'artifact' ? '✨' : reward.type === 'xgen' ? '💎' : reward.type === 'fragments' ? '📜' : dropConfig.emoji}
                      </span>
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-slate-300 font-medium truncate">
                          {reward.type === 'xgen' ? 'XGen' : reward.type === 'fragments' ? 'Фрагменты' : reward.type === 'artifact' ? `Артефакт T${reward.tier ?? 1}` : dropConfig.label}
                        </span>
                        {reward.quantity && reward.quantity > 1 && (
                          <span className="text-[9px] font-mono text-slate-400 bg-white/5 px-1 py-0.5 rounded">
                            ×{reward.quantity}
                          </span>
                        )}
                        {isGuaranteed && (
                          <span className="text-[9px] font-display uppercase tracking-wider px-1.5 py-0.5 rounded border text-green-400 border-green-500/30 bg-green-500/10">
                            ✓ Гарантировано
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="shrink-0 w-14 text-right">
                      <div className="flex items-center justify-end gap-1 mb-0.5">
                        <span className="text-[11px] font-mono font-bold tabular-nums" style={{ color: style.color }}>
                          {chancePct}%
                        </span>
                      </div>
                      <div className="h-1 bg-space-900/50 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full rounded-full"
                          style={{ backgroundColor: style.color }}
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.min(chancePct, 100)}%` }}
                          transition={{ duration: 0.6, delay: idx * 0.04, ease: 'easeOut' }}
                        />
                      </div>
                      <span className="text-[9px] uppercase tracking-wider block mt-0.5 text-right" style={{ color: style.color }}>
                        {style.label}
                      </span>
                    </div>
                  </motion.div>
                )
              })}

              {isAdmin && (
                <div className="pt-1">
                  <button
                    onClick={handleSimulate}
                    disabled={simulating}
                    className="flex items-center gap-1.5 w-full justify-center py-1.5 rounded-lg border border-dashed border-amber-500/20 text-[10px] font-display uppercase tracking-wider text-amber-400/60 hover:text-amber-400 hover:border-amber-500/40 transition-all disabled:opacity-40"
                  >
                    <FlaskConical size={11} />
                    {simulating ? 'Симулируем...' : 'Симулировать ×100'}
                  </button>
                </div>
              )}

              {simError && (
                <p className="text-[10px] text-red-400 text-center">{simError}</p>
              )}

              <AnimatePresence>
                {simResults && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="bg-space-900/60 border border-amber-500/15 rounded-lg p-2.5 mt-1 space-y-1">
                      <p className="text-[9px] font-display uppercase tracking-wider text-amber-400/50 mb-1.5">
                        Результаты ×100
                      </p>
                      {simResults.map((r, i) => {
                        const style = getChanceBadgeStyle(r.percentage)
                        return (
                          <div key={`${r.item_id ?? r.drop_type}-${i}`} className="flex items-center gap-2 text-[10px]">
                            <span className="text-slate-400 truncate flex-1 min-w-0">
                              {r.item_name || r.drop_type}
                              {r.total_xgen ? ` (${r.total_xgen} 💎)` : ''}
                              {r.total_fragments ? ` (${r.total_fragments} 📜)` : ''}
                            </span>
                            <span className="font-mono font-bold tabular-nums" style={{ color: style.color }}>
                              {r.percentage}%
                            </span>
                            <span className="text-slate-600 font-mono">
                              ({r.total_dropped}×)
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
