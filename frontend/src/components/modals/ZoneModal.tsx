import { memo } from 'react'
import type { GalaxyZoneConfig } from '../../types'
import { TIER_TO_RARITY } from '../../types'
import { useI18n } from '../../hooks/useI18n'

interface ZoneModalProps {
  zone: GalaxyZoneConfig
  onClose: () => void
  language: 'ru' | 'en' | 'la'
}

const ZoneModal = memo(({ zone, onClose, language }: ZoneModalProps) => {
  const { t } = useI18n()
  const rarity = TIER_TO_RARITY[zone.tier] || 'common'

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white">{zone.name[language]}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            ✕
          </button>
        </div>

        <div className={`aspect-video bg-cosmic-bg rounded-xl overflow-hidden mb-4 border border-rarity-${rarity}`}>
          <div className="w-full h-full flex items-center justify-center text-5xl">
            {zone.tier <= 2 ? '🌑' : zone.tier === 3 ? '🌒' : zone.tier === 4 ? '🌓' : '🌕'}
          </div>
        </div>

        <div className="space-y-3">
          <span className={`badge bg-rarity-${rarity}/20 text-rarity-${rarity}`}>
            {t('misc.tier')} {zone.tier}
          </span>

          {zone.lore && (
            <p className="text-sm text-gray-300 italic">
              {typeof zone.lore === 'string' ? zone.lore : zone.lore[language] || zone.lore.en || ''}
            </p>
          )}

          <div>
            <h4 className="text-sm font-semibold text-white mb-2">{t('zone.drop.table')}</h4>
            <div className="space-y-1">
              {zone.drop_table.map((item) => (
                <div
                  key={item}
                  className="flex items-center justify-between bg-cosmic-bg rounded-lg px-3 py-2 text-sm"
                >
                  <span className="text-gray-300 font-mono text-xs">{item}</span>
                  <span className="text-gray-500 text-xs">?</span>
                </div>
              ))}
            </div>
          </div>

          <button className="btn-primary w-full mt-4">
            {t('zone.launch')}
          </button>
        </div>
      </div>
    </div>
  )
})

ZoneModal.displayName = 'ZoneModal'
export default ZoneModal
