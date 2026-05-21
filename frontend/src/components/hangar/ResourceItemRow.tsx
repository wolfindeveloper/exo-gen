import { motion } from 'framer-motion'
import { Fuel, Essence, Artifact, RepairMat } from '../../types'
import { useI18n } from '../../hooks/useI18n'

interface ResourceItemRowProps {
  item: Fuel | Essence | Artifact | RepairMat
  onClick: () => void
  ownedCount?: number
  language?: 'ru' | 'en' | 'la'
}

const RARITY_STYLES: Record<string, { border: string; bg: string; glow: string; dot: string; text: string }> = {
  common: {
    border: 'border-rarity-common/30',
    bg: 'bg-white/5',
    glow: 'shadow-glow-common',
    dot: 'bg-rarity-common',
    text: 'text-rarity-common',
  },
  uncommon: {
    border: 'border-rarity-uncommon/30',
    bg: 'bg-rarity-uncommon/5',
    glow: 'shadow-glow-uncommon',
    dot: 'bg-rarity-uncommon',
    text: 'text-rarity-uncommon',
  },
  rare: {
    border: 'border-rarity-rare/30',
    bg: 'bg-rarity-rare/5',
    glow: 'shadow-glow-rare',
    dot: 'bg-rarity-rare',
    text: 'text-rarity-rare',
  },
  epic: {
    border: 'border-rarity-epic/30',
    bg: 'bg-rarity-epic/5',
    glow: 'shadow-glow-epic',
    dot: 'bg-rarity-epic',
    text: 'text-rarity-epic',
  },
  legendary: {
    border: 'border-rarity-legendary/30',
    bg: 'bg-rarity-legendary/5',
    glow: 'shadow-glow-legendary',
    dot: 'bg-rarity-legendary',
    text: 'text-rarity-legendary',
  },
}

export function ResourceItemRow({ item, onClick, ownedCount = 0, language = 'ru' }: ResourceItemRowProps) {
  const { t } = useI18n()
  const rarity = RARITY_STYLES[item.rarity || 'common'] || RARITY_STYLES.common
  const name = item.name[language as keyof typeof item.name] || item.name.ru
  const shortDesc = (item as any).short_description?.[language as keyof typeof item.name] || ''
  const desc = item.description[language as keyof typeof item.description] || item.description.ru
  const displayDesc = shortDesc || (desc.length > 40 ? desc.slice(0, 40) + '...' : desc)

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
      onClick={onClick}
      className={`relative flex items-center gap-3 px-4 py-3 rounded-xl border ${rarity.border} ${rarity.bg} cursor-pointer hover:${rarity.glow} transition-all group`}
    >
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold ${rarity.bg} border ${rarity.border}`}>
        <div className={`w-2 h-2 rounded-full ${rarity.dot}`} />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold truncate ${item.rarity === 'rare' || item.rarity === 'epic' || item.rarity === 'legendary' ? 'bg-gradient-to-r from-neon-cyan to-purple-400 bg-clip-text text-transparent' : 'text-white'}`}>
            {name}
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-gray-400 font-medium">
            {t('misc.tier')}{item.tier}
          </span>
        </div>
        <p className="text-[11px] text-gray-400 truncate">{displayDesc}</p>
      </div>

      {ownedCount > 0 && (
        <span className="text-xs font-bold text-neon-cyan px-2 py-1 rounded-lg bg-neon-cyan/10">
          {ownedCount}
        </span>
      )}
    </motion.div>
  )
}
