/**
 * Интерактивная космическая карта галактики.
 * Полноэкранный контейнер с TierSelector и MapTransition.
 * Звёздное поле рендерится на уровне страницы (UniversePage).
 */

import { useState } from 'react'
import type { GalaxyZoneConfig } from '../../types'
import { useI18n } from '../../hooks/useI18n'
import { TierSelector } from './TierSelector'
import { MapTransition } from './MapTransition'

interface CosmicMapProps {
  zones: GalaxyZoneConfig[]
  onZoneClick: (slug: string) => void
}

export function CosmicMap({ zones, onZoneClick }: CosmicMapProps) {
  const { t } = useI18n()
  const [activeTier, setActiveTier] = useState(1)

  return (
    <div className="relative w-full h-[calc(100vh-12rem)] rounded-2xl overflow-hidden border border-cosmic-border bg-cosmic-bg/50 backdrop-blur-sm">
      {/* Основной контент карты */}
      <div className="relative z-10 flex h-full">
        {/* Область карты */}
        <div className="flex-1 relative">
          <MapTransition
            zones={zones}
            activeTier={activeTier}
            onZoneClick={onZoneClick}
          />
        </div>

        {/* Селектор тиров справа */}
        <div className="flex flex-col items-center justify-center pr-4">
          <TierSelector activeTier={activeTier} onChange={setActiveTier} />
        </div>
      </div>

      {/* Подсказка */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 pointer-events-none">
        <span className="text-[10px] text-gray-400 bg-black/40 px-3 py-1 rounded-full backdrop-blur-sm">
          {t('map.hint')}
        </span>
      </div>
    </div>
  )
}
