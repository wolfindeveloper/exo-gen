import { memo } from 'react'
import { motion } from 'framer-motion'
import { Zap, Gem, Star } from 'lucide-react'
import { Essence, Artifact } from '../../types'
import { BonusBadge } from './BonusBadge'
import { useI18n } from '../../hooks/useI18n'

interface ResourceCardProps {
  item: Essence | Artifact
  onClick: () => void
  ownedCount?: number
  language?: 'ru' | 'en' | 'la'
}

const RARITY_STYLES: Record<string, { border: string; bgGradient: string; glow: string; badge: string }> = {
  common: {
    border: 'border-rarity-common/30',
    bgGradient: 'from-rarity-common/5',
    glow: 'shadow-glow-common',
    badge: 'bg-rarity-common/20 text-rarity-common',
  },
  uncommon: {
    border: 'border-rarity-uncommon/40',
    bgGradient: 'from-rarity-uncommon/10',
    glow: 'shadow-glow-uncommon',
    badge: 'bg-rarity-uncommon/20 text-rarity-uncommon',
  },
  rare: {
    border: 'border-rarity-rare/40',
    bgGradient: 'from-rarity-rare/10',
    glow: 'shadow-glow-rare',
    badge: 'bg-rarity-rare/20 text-rarity-rare',
  },
  epic: {
    border: 'border-rarity-epic/50',
    bgGradient: 'from-rarity-epic/15',
    glow: 'shadow-glow-epic',
    badge: 'bg-rarity-epic/20 text-rarity-epic',
  },
  legendary: {
    border: 'border-rarity-legendary/60',
    bgGradient: 'from-rarity-legendary/20',
    glow: 'shadow-glow-legendary',
    badge: 'bg-rarity-legendary/20 text-rarity-legendary',
  },
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  essence: <Gem className="w-8 h-8" />,
  artifact: <Star className="w-8 h-8" />,
}

export const ResourceCard = memo(function ResourceCard({ item, onClick, ownedCount = 0, language = 'ru' }: ResourceCardProps) {
  const { t } = useI18n()
  const rarity = RARITY_STYLES[item.rarity] || RARITY_STYLES.common
  const name = item.name[language as keyof typeof item.name] || item.name.ru
  const desc = item.description[language as keyof typeof item.description] || item.description.ru
  const truncatedDesc = desc.length > 60 ? desc.slice(0, 60) + '...' : desc

  const isArtifact = item.type === 'artifact'

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`relative rounded-2xl border ${rarity.border} bg-gradient-to-br ${rarity.bgGradient} to-transparent backdrop-blur-xl overflow-hidden cursor-pointer group`}
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${rarity.bgGradient} to-transparent opacity-0 group-hover:opacity-100 transition-opacity`} />

      <div className="relative p-4">
        {/* Art placeholder */}
        <div className="relative w-full aspect-video rounded-xl overflow-hidden bg-cosmic-bg/80 border border-white/10 mb-3 group-hover:scale-[1.02] transition-transform">
          <div className={`absolute inset-0 bg-gradient-to-br ${rarity.bgGradient} to-cosmic-bg/50`} />
          <div className="absolute inset-0 flex items-center justify-center text-white/30">
            {TYPE_ICONS[item.type]}
          </div>
          {item.rarity === 'legendary' && (
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
              animate={{ x: ['-100%', '200%'] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            />
          )}
        </div>

        {/* Name */}
        <h3 className={`text-sm font-bold mb-1 ${item.rarity === 'rare' || item.rarity === 'epic' || item.rarity === 'legendary' ? 'bg-gradient-to-r from-neon-cyan to-purple-400 bg-clip-text text-transparent' : 'text-white'}`}>
          {name}
        </h3>

        {/* Description */}
        <p className="text-[11px] text-gray-400 mb-3 line-clamp-2">{truncatedDesc}</p>

        {/* Footer */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-gray-400 font-medium">
              T{item.tier}
            </span>
            <span className={`text-[10px] px-2 py-0.5 rounded-full ${rarity.badge} font-medium uppercase`}>
              {item.rarity === 'common' ? t('rarity.common') : item.rarity === 'uncommon' ? t('rarity.uncommon') : item.rarity === 'rare' ? t('rarity.rare') : item.rarity === 'epic' ? t('rarity.epic') : t('rarity.legendary')}
            </span>
          </div>

          {isArtifact && (item as Artifact).bonus && (
            <BonusBadge bonus={(item as Artifact).bonus} language={language} />
          )}
        </div>

        {ownedCount > 0 && (
          <div className="absolute top-2 right-2 text-xs font-bold text-neon-cyan px-2 py-1 rounded-lg bg-neon-cyan/10 border border-neon-cyan/30">
            {ownedCount}
          </div>
        )}
      </div>
    </motion.div>
  )
})
