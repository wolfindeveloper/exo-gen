import { motion } from 'framer-motion'

interface SpaceshipProps {
  tier: number
}

const TIER_COLORS: Record<number, { primary: string; secondary: string; accent: string }> = {
  1: { primary: '#9CA3AF', secondary: '#6B7280', accent: '#D1D5DB' },
  2: { primary: '#22C55E', secondary: '#16A34A', accent: '#86EFAC' },
  3: { primary: '#3B82F6', secondary: '#2563EB', accent: '#93C5FD' },
  4: { primary: '#A855F7', secondary: '#9333EA', accent: '#D8B4FE' },
  5: { primary: '#F59E0B', secondary: '#D97706', accent: '#FCD34D' },
}

export function Spaceship({ tier }: SpaceshipProps) {
  const colors = TIER_COLORS[tier] || TIER_COLORS[1]

  return (
    <div className="relative flex flex-col items-center justify-center">
      <motion.div
        animate={{ y: [0, -12, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        className="relative"
      >
        <div className="absolute inset-0 blur-2xl opacity-60">
          <svg width="140" height="160" viewBox="0 0 140 160" fill="none">
            <polygon points="70,10 130,140 70,115 10,140" fill={`url(#glow-${tier})`} />
            <defs>
              <linearGradient id={`glow-${tier}`} x1="70" y1="10" x2="70" y2="140">
                <stop offset="0%" stopColor={colors.primary} />
                <stop offset="100%" stopColor={colors.secondary} />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <svg width="140" height="160" viewBox="0 0 140 160" fill="none" className="relative z-10">
          <defs>
            <linearGradient id={`ship-${tier}`} x1="70" y1="10" x2="70" y2="140">
              <stop offset="0%" stopColor={colors.primary} />
              <stop offset="50%" stopColor={colors.secondary} />
              <stop offset="100%" stopColor={colors.secondary} />
            </linearGradient>
            <linearGradient id={`stroke-${tier}`} x1="70" y1="10" x2="70" y2="140">
              <stop offset="0%" stopColor={colors.primary} />
              <stop offset="100%" stopColor={colors.accent} />
            </linearGradient>
            <filter id={`neon-${tier}`} x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <polygon
            points="70,15 125,130 70,105 15,130"
            fill={`url(#ship-${tier})`}
            stroke={`url(#stroke-${tier})`}
            strokeWidth="2"
            filter={`url(#neon-${tier})`}
          />
          <line x1="70" y1="20" x2="70" y2="100" stroke={colors.primary} strokeWidth="2" opacity="0.8" />
          <line x1="45" y1="80" x2="70" y2="60" stroke={colors.primary} strokeWidth="1.5" opacity="0.6" />
          <line x1="95" y1="80" x2="70" y2="60" stroke={colors.primary} strokeWidth="1.5" opacity="0.6" />
          <ellipse cx="70" cy="50" rx="12" ry="18" fill="#0B0F19" stroke={colors.primary} strokeWidth="1.5" />
          <ellipse cx="70" cy="48" rx="6" ry="10" fill={colors.secondary} opacity="0.8" />
        </svg>
      </motion.div>

      <motion.div
        animate={{ y: [0, -12, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        className="relative -mt-4"
      >
        <motion.svg
          width="60"
          height="80"
          viewBox="0 0 60 80"
          fill="none"
          animate={{ scaleY: [1, 1.15, 0.9, 1.1, 1], opacity: [0.9, 1, 0.8, 1, 0.9] }}
          transition={{ duration: 0.3, repeat: Infinity, ease: 'easeInOut' }}
        >
          <defs>
            <linearGradient id={`flame-${tier}`} x1="30" y1="0" x2="30" y2="80">
              <stop offset="0%" stopColor="#ffd700" />
              <stop offset="30%" stopColor="#ff9500" />
              <stop offset="60%" stopColor={colors.primary} />
              <stop offset="100%" stopColor="transparent" />
            </linearGradient>
            <filter id={`flameGlow-${tier}`} x="-100%" y="-50%" width="300%" height="200%">
              <feGaussianBlur stdDeviation="4" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <ellipse cx="30" cy="35" rx="15" ry="35" fill={`url(#flame-${tier})`} filter={`url(#flameGlow-${tier})`} />
          <ellipse cx="30" cy="25" rx="8" ry="20" fill="#ffffff" opacity="0.6" />
        </motion.svg>
      </motion.div>
    </div>
  )
}
