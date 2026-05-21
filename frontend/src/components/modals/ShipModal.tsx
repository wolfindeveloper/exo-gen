import { useState, memo } from 'react'
import { motion } from 'framer-motion'
import type { ShipConfig } from '../../types'
import { TIER_TO_RARITY } from '../../types'
import { Spaceship } from '../Spaceship'
import { useI18n } from '../../hooks/useI18n'

interface ShipModalProps {
  ship: ShipConfig
  onClose: () => void
  language: 'ru' | 'en' | 'la'
}

const RARITY_GLOW: Record<string, string> = {
  common: 'bg-gray-400/30',
  uncommon: 'bg-green-400/30',
  rare: 'bg-cyan-400/30',
  epic: 'bg-purple-400/30',
  legendary: 'bg-yellow-400/30',
}

const ShipModal = memo(({ ship, onClose, language }: ShipModalProps) => {
  const { t } = useI18n()
  const rarity = TIER_TO_RARITY[ship.tier] || 'common'
  const [imageFailed, setImageFailed] = useState(false)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white">{ship.name[language]}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            ✕
          </button>
        </div>

        <div className={`aspect-square bg-cosmic-bg rounded-xl overflow-hidden mb-4 border border-rarity-${rarity} relative`}>
          {ship.art_path && !imageFailed ? (
            <div className="relative flex items-center justify-center w-full h-full">
              <div className={`absolute inset-0 blur-3xl opacity-40 ${RARITY_GLOW[rarity] || RARITY_GLOW.common}`} />
              <motion.div
                animate={{ y: [0, -15, 0] }}
                transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
                className="relative z-10 w-48 h-48"
              >
                <img
                  src={ship.art_path}
                  alt={ship.name.ru || ship.name.en}
                  className="w-full h-full object-contain drop-shadow-2xl"
                  loading="lazy"
                  onError={() => setImageFailed(true)}
                />
              </motion.div>
            </div>
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Spaceship tier={ship.tier} />
            </div>
          )}
        </div>

        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className={`badge bg-rarity-${rarity}/20 text-rarity-${rarity}`}>
              {t('misc.tier')} {ship.tier} · {rarity === 'common' ? t('rarity.common') : rarity === 'uncommon' ? t('rarity.uncommon') : rarity === 'rare' ? t('rarity.rare') : rarity === 'epic' ? t('rarity.epic') : t('rarity.legendary')}
            </span>
            {ship.is_nft && (
              <span className="badge bg-neon-purple/20 text-neon-purple">{t('ship.nft')}</span>
            )}
          </div>

          <p className="text-sm text-gray-300">
            {ship.description[language] || ship.description.ru}
          </p>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-cosmic-bg rounded-lg p-3">
              <p className="text-gray-400 text-xs">{t('ship.modal.stability')}</p>
              <p className="text-white font-semibold">{ship.base_stability}%</p>
            </div>
            <div className="bg-cosmic-bg rounded-lg p-3">
              <p className="text-gray-400 text-xs">{t('ship.modal.slots')}</p>
              <p className="text-white font-semibold">{ship.expedition_slots}</p>
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button className="btn-primary flex-1">
              {t('ship.modal.launch')}
            </button>
            <button className="btn-danger flex-1">
              {t('ship.modal.repair')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
})

ShipModal.displayName = 'ShipModal'
export default ShipModal
