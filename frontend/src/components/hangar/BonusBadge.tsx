import { motion } from 'framer-motion'

interface BonusBadgeProps {
  bonus: { type: string; value: number; display: { ru: string; en: string; la?: string } }
  language?: 'ru' | 'en' | 'la'
}

const BONUS_COLORS: Record<string, string> = {
  expedition_yield: 'from-neon-cyan/20 to-cyan-600/20 text-neon-cyan border-neon-cyan/30',
  risk_reduction: 'from-green-500/20 to-green-600/20 text-neon-green border-neon-green/30',
  damage_reduction: 'from-green-500/20 to-green-600/20 text-neon-green border-neon-green/30',
  expedition_speed: 'from-yellow-500/20 to-yellow-600/20 text-yellow-400 border-yellow-500/30',
  rare_chance: 'from-purple-500/20 to-purple-600/20 text-neon-purple border-neon-purple/30',
  t5_access: 'from-rarity-legendary/20 to-yellow-600/20 text-rarity-legendary border-rarity-legendary/30',
}

export function BonusBadge({ bonus, language = 'ru' }: BonusBadgeProps) {
  const colorKey = bonus.type in BONUS_COLORS ? bonus.type : 'expedition_yield'
  const colors = BONUS_COLORS[colorKey]
  const displayText = bonus.display[language as keyof typeof bonus.display] || bonus.display.ru
  const isRare = bonus.value >= 15

  return (
    <motion.div
      className={`px-2 py-0.5 rounded-full text-[10px] font-bold bg-gradient-to-r ${colors} border`}
      animate={isRare ? { scale: [1, 1.05, 1] } : {}}
      transition={isRare ? { duration: 2, repeat: Infinity, ease: 'easeInOut' } : {}}
    >
      {displayText}
    </motion.div>
  )
}
