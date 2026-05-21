import { motion, AnimatePresence } from 'framer-motion'
import { X, Shield, Zap, Gem, Star, AlertTriangle, Wrench } from 'lucide-react'
import toast from 'react-hot-toast'
import { Fuel, Essence, Artifact, RepairMat, ResourceItem } from '../../types'
import { BonusBadge } from './BonusBadge'
import { useI18n } from '../../hooks/useI18n'

interface ResourceDetailModalProps {
  item: ResourceItem | null
  onClose: () => void
  language?: 'ru' | 'en' | 'la'
}

const RARITY_STYLES: Record<string, { border: string; badge: string; gradient: string }> = {
  common: {
    border: 'border-rarity-common/40',
    badge: 'bg-rarity-common/20 text-rarity-common border-rarity-common/30',
    gradient: 'from-rarity-common/10',
  },
  uncommon: {
    border: 'border-rarity-uncommon/40',
    badge: 'bg-rarity-uncommon/20 text-rarity-uncommon border-rarity-uncommon/30',
    gradient: 'from-rarity-uncommon/10',
  },
  rare: {
    border: 'border-rarity-rare/40',
    badge: 'bg-rarity-rare/20 text-rarity-rare border-rarity-rare/30',
    gradient: 'from-rarity-rare/10',
  },
  epic: {
    border: 'border-rarity-epic/50',
    badge: 'bg-rarity-epic/20 text-rarity-epic border-rarity-epic/30',
    gradient: 'from-rarity-epic/15',
  },
  legendary: {
    border: 'border-rarity-legendary/60',
    badge: 'bg-rarity-legendary/20 text-rarity-legendary border-rarity-legendary/30',
    gradient: 'from-rarity-legendary/20',
  },
}

export function ResourceDetailModal({ item, onClose, language = 'ru' }: ResourceDetailModalProps) {
  const { t } = useI18n()
  if (!item) return null

  const rarity = RARITY_STYLES[item.rarity || 'common'] || RARITY_STYLES.common
  const name = item.name[language as keyof typeof item.name] || item.name.ru
  const desc = item.description[language as keyof typeof item.description] || item.description.ru
  const lore = item.lore[language as keyof typeof item.lore] || item.lore.ru

  const isFuel = item.type === 'fuel'
  const isEssence = item.type === 'essence'
  const isArtifact = item.type === 'artifact'
  const isRepairMat = item.type === 'repair_mat'

  const handleActionClick = () => {
    if (isEssence) {
      toast(t('resource.toast.essence'), { icon: '🔬' })
    } else if (isFuel) {
      toast(t('resource.toast.fuel'), { icon: '⛽' })
    } else if (isRepairMat) {
      toast(t('resource.toast.repair'), { icon: '🔧' })
    } else {
      toast(t('resource.toast.artifact'), { icon: '🛡️' })
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[80] flex items-center justify-center p-3"
        onClick={onClose}
      >
        <div className="absolute inset-0 bg-black/80 backdrop-blur-md" />

        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="relative w-full max-w-lg max-h-[85vh] bg-cosmic-bg border border-cosmic-border rounded-3xl overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="relative px-5 pt-5 pb-3 border-b border-cosmic-border">
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-xl hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>

            <h2 className={`text-lg font-bold bg-gradient-to-r ${rarity.gradient} to-transparent bg-clip-text text-transparent pr-12`}>
              {name}
            </h2>

            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-400 font-medium">
                {t('misc.tier')} {item.tier}
              </span>
              <span className={`text-xs px-2 py-0.5 rounded-full border font-medium uppercase ${rarity.badge}`}>
                {item.rarity === 'common' ? t('rarity.common') : item.rarity === 'uncommon' ? t('rarity.uncommon') : item.rarity === 'rare' ? t('rarity.rare') : item.rarity === 'epic' ? t('rarity.epic') : t('rarity.legendary')}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-400 font-medium">
                {item.type === 'fuel' ? t('resource.detail.type.fuel') : item.type === 'essence' ? t('resource.detail.type.essence') : item.type === 'artifact' ? t('resource.detail.type.artifact') : t('resource.detail.type.repair')}
              </span>
            </div>
          </div>

          {/* Scrollable content */}
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
            {/* Art placeholder */}
            <div className="relative w-full aspect-video rounded-xl overflow-hidden bg-cosmic-bg border border-cosmic-border">
              <div className={`absolute inset-0 bg-gradient-to-br ${rarity.gradient} to-cosmic-bg/50`} />
              <div className="absolute inset-0 flex items-center justify-center text-white/20">
                {isFuel && <Zap className="w-16 h-16" />}
                {isEssence && <Gem className="w-16 h-16" />}
                {isArtifact && <Star className="w-16 h-16" />}
                {isRepairMat && <Wrench className="w-16 h-16" />}
              </div>
              {item.rarity === 'legendary' && (
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
                  animate={{ x: ['-100%', '200%'] }}
                  transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                />
              )}
            </div>

            {/* Description */}
            <div>
              <h3 className="text-sm font-bold text-white mb-2">{t('resource.detail.description')}</h3>
              <p className="text-sm text-gray-300 leading-relaxed">{desc}</p>
            </div>

            {/* Lore */}
            {lore && (
              <div>
                <h3 className="text-sm font-bold text-white mb-2">{t('resource.detail.lore')}</h3>
                <div className="px-4 py-3 rounded-xl bg-white/5 border border-cosmic-border italic text-sm text-gray-400 leading-relaxed">
                  {lore}
                </div>
              </div>
            )}

            {/* Stats Grid */}
            {isFuel && (
              <div>
                <h3 className="text-sm font-bold text-white mb-2">{t('resource.detail.stats')}</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                      <Zap className="w-4 h-4 text-neon-cyan" />
                      <span className="text-[10px] uppercase tracking-widest text-gray-500 font-medium">{t('resource.detail.efficiency')}</span>
                    </div>
                    <span className="text-lg font-bold text-neon-cyan">{(item as Fuel).stats.efficiency}%</span>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertTriangle className="w-4 h-4 text-yellow-400" />
                      <span className="text-[10px] uppercase tracking-widest text-gray-500 font-medium">{t('resource.detail.consumption')}</span>
                    </div>
                    <span className="text-lg font-bold text-yellow-400">{(item as Fuel).stats.burn_rate}x</span>
                  </div>
                </div>
              </div>
            )}

            {isEssence && (
              <div>
                <h3 className="text-sm font-bold text-white mb-2">{t('resource.detail.stats')}</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                      <Gem className="w-4 h-4 text-neon-purple" />
                      <span className="text-[10px] uppercase tracking-widest text-gray-500 font-medium">{t('resource.detail.domain')}</span>
                    </div>
                    <span className="text-sm font-bold text-neon-purple capitalize">{(item as Essence).domain}</span>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                      <Shield className="w-4 h-4 text-gray-400" />
                      <span className="text-[10px] uppercase tracking-widest text-gray-500 font-medium">{t('resource.detail.weight')}</span>
                    </div>
                    <span className="text-lg font-bold text-gray-300">{(item as Essence).crafting_weight}</span>
                  </div>
                </div>
              </div>
            )}

            {isArtifact && (
              <div>
                <h3 className="text-sm font-bold text-white mb-2">{t('resource.detail.bonus')}</h3>
                <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10">
                  <BonusBadge bonus={(item as Artifact).bonus} language={language} />
                </div>
              </div>
            )}

            {isRepairMat && (
              <div>
                <h3 className="text-sm font-bold text-white mb-2">{t('resource.detail.stats')}</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                      <Wrench className="w-4 h-4 text-neon-cyan" />
                      <span className="text-[10px] uppercase tracking-widest text-gray-500 font-medium">{t('resource.detail.restoration')}</span>
                    </div>
                    <span className="text-lg font-bold text-neon-cyan">{(item as RepairMat).repair_value}%</span>
                  </div>
                  <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                      <Shield className="w-4 h-4 text-gray-400" />
                      <span className="text-[10px] uppercase tracking-widest text-gray-500 font-medium">{t('resource.detail.full.repair')}</span>
                    </div>
                    <span className="text-lg font-bold text-gray-300">{Math.ceil(100 / (item as RepairMat).repair_value)} {t('resource.detail.pcs')}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Action button */}
          <div className="px-5 py-4 border-t border-cosmic-border">
            <button
              onClick={handleActionClick}
              className={`relative w-full min-h-[44px] rounded-xl font-bold text-white text-sm overflow-hidden bg-gradient-to-r ${rarity.gradient} to-transparent border ${rarity.border} hover:opacity-80 transition-opacity`}
            >
              {isFuel && t('resource.action.fuel')}
              {isEssence && t('resource.action.essence')}
              {isArtifact && t('resource.action.artifact')}
              {isRepairMat && t('resource.action.repair')}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
