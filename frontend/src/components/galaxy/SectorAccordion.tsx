/**
 * Компонент аккордеона секторов галактики.
 * Группирует зоны по тиру (T1-T5), сворачиваемые секции.
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Shield } from 'lucide-react'
import type { GalaxyZoneConfig } from '../../types'
import { ZoneCardCompact } from './ZoneCardCompact'
import { useI18n } from '../../hooks/useI18n'

const TIER_ICONS: Record<number, string> = {
  1: '🌑',
  2: '🌠',
  3: '⭐',
  4: '🔥',
  5: '💫',
}

const TIER_NAMES: Record<number, string> = {
  1: 'sector.tier1',
  2: 'sector.tier2',
  3: 'sector.tier3',
  4: 'sector.tier4',
  5: 'sector.tier5',
}

interface SectorAccordionProps {
  zones: GalaxyZoneConfig[]
  onZoneClick: (slug: string) => void
  language?: 'ru' | 'en' | 'la'
}

export function SectorAccordion({ zones, onZoneClick, language = 'ru' }: SectorAccordionProps) {
  const { t } = useI18n()
  // Группируем зоны по тиру
  const zonesByTier = zones.reduce<Record<number, GalaxyZoneConfig[]>>((acc, zone) => {
    const tier = zone.tier || 1
    if (!acc[tier]) acc[tier] = []
    acc[tier].push(zone)
    return acc
  }, {})

  // По умолчанию T1 раскрыт, остальные свёрнуты
  const [expandedTier, setExpandedTier] = useState<number>(1)

  const toggleTier = (tier: number) => {
    setExpandedTier((prev) => (prev === tier ? -1 : tier))
  }

  return (
    <div className="flex flex-col gap-3 mt-4">
      {[1, 2, 3, 4, 5].map((tier) => {
        const tierZones = zonesByTier[tier] || []
        const isExpanded = expandedTier === tier
        const icon = TIER_ICONS[tier] || '🌌'
        const tierName = t(TIER_NAMES[tier] as any) || `${t('misc.tier')} ${tier}`

        return (
          <motion.div
            key={tier}
            className="rounded-2xl overflow-hidden border border-cosmic-border bg-white/5 backdrop-blur-xl"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: tier * 0.05 }}
          >
            {/* Заголовок тира */}
            <button
              onClick={() => toggleTier(tier)}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-xl">{icon}</span>
                <div className="text-left">
                  <p className="text-sm font-bold text-white">{t('misc.tier')} {tier}</p>
                  <p className="text-[10px] text-gray-400">{tierName}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">{tierZones.length} {t('sector.zones')}</span>
                <motion.div
                  animate={{ rotate: isExpanded ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </motion.div>
              </div>
            </button>

            {/* Содержимое тира */}
            <AnimatePresence>
              {isExpanded && tierZones.length > 0 && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25, ease: 'easeInOut' }}
                  className="overflow-hidden"
                >
                  <div className="px-3 pb-3 flex flex-col gap-2">
                    {tierZones.map((zone) => (
                      <ZoneCardCompact
                        key={zone.slug}
                        zone={zone}
                        onClick={() => onZoneClick(zone.slug)}
                        language={language}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )
      })}
    </div>
  )
}
