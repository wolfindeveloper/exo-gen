/**
 * Обёртка для анимированного переключения тиров на карте.
 * Fade out старых зон, staggered fade in новых.
 */

import { AnimatePresence, motion } from 'framer-motion'
import type { GalaxyZoneConfig } from '../../types'
import { ZoneIcon } from './ZoneIcon'

interface MapTransitionProps {
  zones: GalaxyZoneConfig[]
  activeTier: number
  onZoneClick: (slug: string) => void
}

export function MapTransition({ zones, activeTier, onZoneClick }: MapTransitionProps) {
  const filteredZones = zones.filter((z) => z.tier === activeTier)

  // Позиции для зон на карте (расположение по кругу)
  // Радиус ограничен чтобы зоны не выходили за границы контейнера
  const getZonePosition = (index: number, total: number): React.CSSProperties => {
    if (total === 0) return {}
    const angle = (index / total) * Math.PI * 2 - Math.PI / 2
    // Радиус растёт с тиром, но ограничен 38% чтобы иконки оставались в пределах контейнера
    const maxRadius = 38
    const radius = 18 + Math.min(activeTier * 4, maxRadius - 18)
    const x = 50 + Math.cos(angle) * radius
    const y = 50 + Math.sin(angle) * radius
    return {
      left: `${x}%`,
      top: `${y}%`,
      transform: 'translate(-50%, -50%)',
    }
  }

  return (
    <div className="relative w-full h-full">
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTier}
          className="absolute inset-0"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          {filteredZones.map((zone, i) => (
            <motion.div
              key={zone.slug}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{
                duration: 0.3,
                delay: i * 0.1,
                ease: 'easeOut',
              }}
            >
              <ZoneIcon
                zone={zone}
                onClick={() => onZoneClick(zone.slug)}
                style={getZonePosition(i, filteredZones.length)}
              />
            </motion.div>
          ))}
        </motion.div>
      </AnimatePresence>

      {/* Центральная точка — ядро галактики */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <motion.div
          className="w-6 h-6 rounded-full bg-neon-cyan"
          style={{ boxShadow: '0 0 30px rgba(6, 182, 212, 0.8), 0 0 60px rgba(6, 182, 212, 0.4)' }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.8, 1, 0.8],
          }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>
    </div>
  )
}
