import { memo } from 'react'
import type { GalaxyZoneConfig } from '../../types'
import { TIER_TO_RARITY } from '../../types'
import { useI18n } from '../../hooks/useI18n'

interface ZoneCardProps {
  zone: GalaxyZoneConfig
  onClick: (slug: string) => void
}

const ZoneCard = memo(({ zone, onClick }: ZoneCardProps) => {
  const { t } = useI18n()
  const rarity = TIER_TO_RARITY[zone.tier] || 'common'

  return (
    <button
      onClick={() => onClick(zone.slug)}
      className={`card card-hover border-l-4 border-l-rarity-${rarity} shadow-glow-${rarity} w-full text-left`}
    >
      <div className="relative aspect-video bg-cosmic-bg rounded-lg overflow-hidden mb-3">
        <div className="absolute inset-0 flex items-center justify-center text-3xl">
          {zone.tier <= 2 ? '🌑' : zone.tier === 3 ? '🌒' : zone.tier === 4 ? '🌓' : '🌕'}
        </div>
        <div className={`absolute top-2 right-2 badge bg-rarity-${rarity}/20 text-rarity-${rarity}`}>
          T{zone.tier}
        </div>
      </div>

      <h3 className="text-sm font-semibold text-white truncate">
        {zone.name.en}
      </h3>
      <p className="text-xs text-gray-400 mt-1 line-clamp-2">
        {zone.description.ru || t('zone.card.explore')}
      </p>
    </button>
  )
})

ZoneCard.displayName = 'ZoneCard'
export default ZoneCard
