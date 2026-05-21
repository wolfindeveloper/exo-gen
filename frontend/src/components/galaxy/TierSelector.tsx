/**
 * Вертикальный селектор тиров для карты галактики.
 * 5 кнопок (T1 → T5), активный тир с neon glow.
 */

import { motion } from 'framer-motion'

const TIER_ICONS: Record<number, string> = {
  1: '🌑',
  2: '🌠',
  3: '⭐',
  4: '🔥',
  5: '💫',
}

interface TierSelectorProps {
  activeTier: number
  onChange: (tier: number) => void
}

export function TierSelector({ activeTier, onChange }: TierSelectorProps) {
  return (
    <div className="flex flex-col gap-2">
      {[1, 2, 3, 4, 5].map((tier) => {
        const isActive = activeTier === tier
        const icon = TIER_ICONS[tier] || '🌌'

        return (
          <motion.button
            key={tier}
            onClick={() => onChange(tier)}
            className={`relative w-12 h-12 rounded-xl flex items-center justify-center text-xl transition-all ${
              isActive
                ? 'bg-neon-cyan/20 border-2 border-neon-cyan/60 shadow-[0_0_15px_rgba(6,182,212,0.4)]'
                : 'bg-white/5 border border-cosmic-border hover:border-white/20'
            }`}
            whileTap={{ scale: 0.9 }}
          >
            {isActive && (
              <motion.div
                layoutId="tier-selector-glow"
                className="absolute inset-0 rounded-xl bg-neon-cyan/10"
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              />
            )}
            <span className="relative z-10">{icon}</span>
            <span
              className={`absolute -bottom-4 text-[8px] font-bold ${
                isActive ? 'text-neon-cyan' : 'text-gray-500'
              }`}
            >
              T{tier}
            </span>
          </motion.button>
        )
      })}
    </div>
  )
}
