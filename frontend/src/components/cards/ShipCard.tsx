import { memo } from 'react'
import { motion } from 'framer-motion'
import type { ShipConfig } from '../../types'
import { TIER_TO_RARITY } from '../../types'
import { useI18n } from '../../hooks/useI18n'

interface ShipCardProps {
  ship: ShipConfig
  onClick: (slug: string) => void
}

const ShipCard = memo(({ ship, onClick }: ShipCardProps) => {
  const { t } = useI18n()
  const rarity = TIER_TO_RARITY[ship.tier] || 'common'

  return (
    <button
      onClick={() => onClick(ship.slug)}
      className={`card card-hover border-l-4 border-l-rarity-${rarity} shadow-glow-${rarity} w-full text-left`}
    >
      <div className="relative aspect-square bg-cosmic-bg rounded-lg overflow-hidden mb-3">
        <div className="absolute inset-0 flex items-center justify-center text-4xl">
          {ship.tier <= 3 ? '🚀' : ship.tier === 4 ? '⚡' : '🌟'}
        </div>
        <div className={`absolute top-2 left-2 badge bg-rarity-${rarity}/20 text-rarity-${rarity}`}>
          T{ship.tier}
        </div>
        {ship.is_nft && (
          <div className="absolute top-2 right-2 badge bg-neon-purple/20 text-neon-purple">
            {t('ship.nft')}
          </div>
        )}
      </div>

      <h3 className="text-sm font-semibold text-white truncate">
        {ship.name.en}
      </h3>
      <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
        <span>{t('ship.modal.stability')}: {ship.base_stability}%</span>
        <span>{t('ship.modal.slots')}: {ship.expedition_slots}</span>
      </div>
    </button>
  )
})

ShipCard.displayName = 'ShipCard'
export default ShipCard
