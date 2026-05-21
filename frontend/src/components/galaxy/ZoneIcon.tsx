/**
 * Иконка зоны на интерактивной карте.
 * Анимация левитации, neon glow при наведении.
 */

import { motion } from 'framer-motion'
import type { GalaxyZoneConfig } from '../../types'

const TIER_COLORS: Record<number, string> = {
  1: 'rgba(156, 163, 175, 0.6)',
  2: 'rgba(34, 197, 94, 0.6)',
  3: 'rgba(59, 130, 246, 0.6)',
  4: 'rgba(168, 85, 247, 0.6)',
  5: 'rgba(234, 179, 8, 0.6)',
}

const TIER_GLOW: Record<number, string> = {
  1: 'rgba(156, 163, 175, 0.3)',
  2: 'rgba(34, 197, 94, 0.3)',
  3: 'rgba(59, 130, 246, 0.3)',
  4: 'rgba(168, 85, 247, 0.3)',
  5: 'rgba(234, 179, 8, 0.3)',
}

const TIER_EMOJI: Record<number, string> = {
  1: '🪨',
  2: '🌑',
  3: '🌍',
  4: '🔥',
  5: '⭐',
}

interface ZoneIconProps {
  zone: GalaxyZoneConfig
  onClick: () => void
  style?: React.CSSProperties
}

export function ZoneIcon({ zone, onClick, style }: ZoneIconProps) {
  const tier = zone.tier || 1
  const color = TIER_COLORS[tier] || TIER_COLORS[1]
  const glow = TIER_GLOW[tier] || TIER_GLOW[1]
  const emoji = TIER_EMOJI[tier] || '🌌'

  return (
    <motion.button
      onClick={onClick}
      style={{
        ...style,
        position: 'absolute',
      }}
      className="group flex flex-col items-center gap-1"
      animate={{
        y: [0, -8, 0],
      }}
      transition={{
        duration: 4,
        repeat: Infinity,
        ease: 'easeInOut',
        delay: Math.random() * 2,
      }}
      whileHover={{ scale: 1.15 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Neon glow ring */}
      <motion.div
        className="w-14 h-14 rounded-full flex items-center justify-center text-2xl"
        style={{
          background: `radial-gradient(circle, ${glow} 0%, transparent 70%)`,
          border: `2px solid ${color}`,
          boxShadow: `0 0 20px ${glow}`,
        }}
        whileHover={{
          boxShadow: `0 0 30px ${color}, 0 0 60px ${glow}`,
        }}
        transition={{ duration: 0.3 }}
      >
        {emoji}
      </motion.div>

      {/* Название зоны */}
      <span className="text-[9px] text-gray-300 font-medium opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap bg-black/60 px-2 py-0.5 rounded-full backdrop-blur-sm">
        {(zone.name as Record<string, string>)?.ru || zone.slug}
      </span>
    </motion.button>
  )
}
