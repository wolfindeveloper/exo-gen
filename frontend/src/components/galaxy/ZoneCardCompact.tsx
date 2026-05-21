/**
 * Компактная карточка зоны для аккордеона секторов.
 * Использует glassmorphism-стиль из hangar-card.tsx.
 */

import { motion } from 'framer-motion'
import { Shield, AlertTriangle } from 'lucide-react'
import type { GalaxyZoneConfig } from '../../types'
import { useI18n } from '../../hooks/useI18n'

const TIER_COLORS: Record<number, { border: string; text: string; bg: string; glow: string }> = {
  1: { border: 'border-gray-500/30', text: 'text-gray-400', bg: 'bg-gray-500/10', glow: 'shadow-gray-500/20' },
  2: { border: 'border-green-500/30', text: 'text-green-400', bg: 'bg-green-500/10', glow: 'shadow-green-500/20' },
  3: { border: 'border-blue-500/30', text: 'text-blue-400', bg: 'bg-blue-500/10', glow: 'shadow-blue-500/20' },
  4: { border: 'border-purple-500/30', text: 'text-purple-400', bg: 'bg-purple-500/10', glow: 'shadow-purple-500/20' },
  5: { border: 'border-yellow-500/30', text: 'text-yellow-400', bg: 'bg-yellow-500/10', glow: 'shadow-yellow-500/20' },
}

/** Получает цвет бейджа риска */
function getRiskColor(riskPct: number): string {
  if (riskPct < 30) return 'text-green-400'
  if (riskPct < 60) return 'text-yellow-400'
  return 'text-red-400'
}

interface ZoneCardCompactProps {
  zone: GalaxyZoneConfig
  onClick: () => void
  language?: 'ru' | 'en' | 'la'
}

export function ZoneCardCompact({ zone, onClick, language = 'ru' }: ZoneCardCompactProps) {
  const { t } = useI18n()
  const tierColor = TIER_COLORS[zone.tier] || TIER_COLORS[1]
  const riskPct = zone.risk_pct ?? 0
  const riskColor = getRiskColor(riskPct)

  // Получаем название зоны
  const nameObj = zone.name as Record<string, string> | undefined
  const displayName = nameObj?.[language] || nameObj?.en || nameObj?.ru || zone.slug

  // Получаем топ-2 ресурса из loot_table или drop_table
  const lootItems = zone.loot_table
    ? zone.loot_table.slice(0, 2).map((l) => l.essence_slug)
    : (zone.drop_table || []).slice(0, 2)

  return (
    <motion.button
      onClick={onClick}
      whileTap={{ scale: 0.98 }}
      className={`relative w-full bg-white/5 backdrop-blur-xl border ${tierColor.border} rounded-xl p-3 text-left hover:bg-white/10 transition-colors`}
    >
      <div className="flex items-center gap-3">
        {/* Иконка зоны */}
        <div className={`w-10 h-10 rounded-lg ${tierColor.bg} flex items-center justify-center text-lg flex-shrink-0`}>
          {zone.tier <= 2 ? '🌑' : zone.tier === 3 ? '🌒' : zone.tier === 4 ? '🌓' : '🌕'}
        </div>

        {/* Информация */}
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-bold text-white truncate">{displayName}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-[10px] uppercase tracking-wider ${tierColor.text} font-medium`}>
              {t('misc.tier')} {zone.tier}
            </span>
            <span className="text-[10px] text-gray-500">· {lootItems.length} {t('zone.card.resources')}</span>
          </div>
        </div>

        {/* Бейдж риска */}
        <div className="flex items-center gap-1 flex-shrink-0">
          {riskPct > 50 ? (
            <AlertTriangle className={`w-3.5 h-3.5 ${riskColor}`} />
          ) : (
            <Shield className={`w-3.5 h-3.5 ${riskColor}`} />
          )}
          <span className={`text-xs font-bold ${riskColor}`}>{riskPct}%</span>
        </div>
      </div>

      {/* Превью лута */}
      {lootItems.length > 0 && (
        <div className="flex gap-1 mt-2 ml-13">
          {lootItems.map((item) => (
            <span
              key={item}
              className="text-[9px] px-1.5 py-0.5 rounded-full bg-white/5 text-gray-400 border border-white/10 truncate max-w-[100px]"
            >
              {item.replace('essence_', 'E').replace('fuel_', 'F')}
            </span>
          ))}
        </div>
      )}
    </motion.button>
  )
}
