import { memo } from 'react'
import { motion } from 'motion/react'

import { cardHover } from '../lib/animations'
import { canAccessZone, formatUnlockHint } from '../lib/progression'
import type { Zone } from '../types'

interface ZoneCardProps {
  zone: Zone
  onSelect: (zone: Zone) => void
  disabled?: boolean
  index?: number
  playerLevel?: number
}

const tierColors = ['', 'text-neon-cyan', 'text-neon-green', 'text-neon-purple', 'text-neon-amber', 'text-neon-red']
const tierBorders = ['', 'border-neon-cyan/20', 'border-neon-green/20', 'border-neon-purple/20', 'border-neon-amber/20', 'border-neon-red/20']

function lootLabel(loot: Zone['loot_table'][number]): string {
  if (loot.item_type === 'xgen') return 'XGen'
  if (loot.item_type === 'fragments') return 'Фрагменты'
  return loot.item_name || 'Неизвестный предмет'
}

function lootColor(loot: Zone['loot_table'][number]): string {
  if (loot.item_type === 'xgen') return 'text-neon-amber border-neon-amber/20 bg-neon-amber/10'
  if (loot.item_type === 'fragments') return 'text-neon-purple border-neon-purple/20 bg-neon-purple/10'
  return 'text-neon-cyan border-neon-cyan/20 bg-neon-cyan/10'
}

function chanceText(chance: number): string {
  if (chance >= 0.99) return '100%'
  return `${Math.round(chance * 100)}%`
}

export const ZoneCard = memo(function ZoneCard({ zone, onSelect, disabled, index = 0, playerLevel = 1 }: ZoneCardProps) {
  const lootOverflow = zone.loot_table.length > 4
  const zoneTier = zone.tier ?? 1
  const unlockStatus = canAccessZone(playerLevel, zoneTier)
  const isLocked = !unlockStatus.isUnlocked

  if (isLocked) {
    return (
      <motion.button
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.08 }}
        className="glass-card p-4 text-left w-full relative overflow-hidden opacity-50 cursor-not-allowed"
        disabled
      >
        <div className="absolute inset-0 backdrop-blur-[2px] bg-black/30 z-10" />
        <div className="absolute inset-0 flex items-center justify-center z-20">
          <div className="bg-space-900/90 border border-white/10 rounded-2xl px-4 py-3 text-center">
            <div className="text-3xl mb-1">🔒</div>
            <p className="text-[10px] font-display uppercase tracking-wider text-slate-400">
              Требуется уровень {unlockStatus.requiredLevel}
            </p>
            <p className="text-[9px] text-slate-600 mt-0.5">
              {formatUnlockHint(unlockStatus.requiredLevel!, playerLevel)}
            </p>
          </div>
        </div>
        <div className="blur-[2px]">
          <h3 className="font-display text-sm uppercase tracking-wider">{zone.name}</h3>
          <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">{zone.description}</p>
          <div className="flex gap-3 text-[11px] text-slate-500 mt-3">
            <span>⛽ {zone.fuel_cost}</span>
            <span>⏱ {Math.round(zone.duration_seconds / 3600)}ч</span>
          </div>
        </div>
      </motion.button>
    )
  }

  return (
    <motion.button
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, type: 'spring', stiffness: 300, damping: 24 }}
      {...cardHover}
      onClick={() => onSelect(zone)}
      disabled={disabled}
      className={`glass-card p-4 ${tierBorders[zoneTier]} text-left w-full transition disabled:opacity-30 disabled:cursor-not-allowed`}
    >
      <div className="flex justify-between items-start mb-1">
        <h3 className="font-display text-sm uppercase tracking-wider">{zone.name}</h3>
        <span className={`text-[10px] font-medium ${tierColors[zoneTier]}`}>T{zoneTier}</span>
      </div>
      <p className="text-[11px] text-slate-500 mb-3 line-clamp-2">{zone.description}</p>
      <div className="flex gap-3 text-[11px] text-slate-500 mb-3">
        <span>⛽ {zone.fuel_cost}</span>
        <span>⏱ {Math.round(zone.duration_seconds / 3600)}ч</span>
        <span>⚠ {Math.round(zone.optimism_risk * 100)}%</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {zone.loot_table.slice(0, 4).map((loot) => (
          <span
            key={loot.item_id ?? loot.item_type}
            className={`text-[9px] px-2 py-0.5 rounded-full border ${lootColor(loot)}`}
          >
            {lootLabel(loot)} x{loot.amount}шт ({chanceText(loot.chance)})
          </span>
        ))}
        {lootOverflow && (
          <span className="text-[9px] bg-space-700/50 px-2 py-0.5 rounded-full text-slate-500 border border-white/5">
            +{zone.loot_table.length - 4}
          </span>
        )}
      </div>
    </motion.button>
  )
})
