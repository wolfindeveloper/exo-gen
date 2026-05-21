import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Star, Trophy, Gem, ChevronDown, ChevronUp, Filter, Calendar } from 'lucide-react'
import type { Artifact, Essence } from '../../types'
import { useI18n } from '../../hooks/useI18n'

interface DiscoverersListProps {
  artifacts: Record<string, Artifact>
  essences: Record<string, Essence>
  currentPlayerUsername?: string
  language?: 'ru' | 'en' | 'la'
}

type SortMode = 'date' | 'tier' | 'rarity'
type FilterMode = 'all' | 'mine'

const RARITY_ORDER: Record<string, number> = {
  common: 0,
  uncommon: 1,
  rare: 2,
  epic: 3,
  legendary: 4,
}

const RARITY_STYLES: Record<string, { border: string; badge: string; glow: string }> = {
  common: {
    border: 'border-rarity-common/30',
    badge: 'bg-rarity-common/20 text-rarity-common',
    glow: 'shadow-glow-common',
  },
  uncommon: {
    border: 'border-rarity-uncommon/30',
    badge: 'bg-rarity-uncommon/20 text-rarity-uncommon',
    glow: 'shadow-glow-uncommon',
  },
  rare: {
    border: 'border-rarity-rare/40',
    badge: 'bg-rarity-rare/20 text-rarity-rare',
    glow: 'shadow-glow-rare',
  },
  epic: {
    border: 'border-rarity-epic/50',
    badge: 'bg-rarity-epic/20 text-rarity-epic',
    glow: 'shadow-glow-epic',
  },
  legendary: {
    border: 'border-rarity-legendary/60',
    badge: 'bg-rarity-legendary/20 text-rarity-legendary',
    glow: 'shadow-glow-legendary',
  },
}

export function DiscoverersList({ artifacts, essences, currentPlayerUsername = '', language = 'ru' }: DiscoverersListProps) {
  const { t } = useI18n()
  const [filterMode, setFilterMode] = useState<FilterMode>('all')
  const [sortMode, setSortMode] = useState<SortMode>('date')

  const discoveredArtifacts = useMemo(() => {
    let list = Object.values(artifacts).filter((a) => a.is_discovered)

    if (filterMode === 'mine') {
      list = list.filter((a) => a.discovered_by.includes(currentPlayerUsername))
    }

    list.sort((a, b) => {
      if (sortMode === 'date') {
        const dateA = a.discovered_at ? new Date(a.discovered_at).getTime() : 0
        const dateB = b.discovered_at ? new Date(b.discovered_at).getTime() : 0
        return dateB - dateA
      }
      if (sortMode === 'tier') {
        return b.tier - a.tier
      }
      return RARITY_ORDER[b.rarity] - RARITY_ORDER[a.rarity]
    })

    return list
  }, [artifacts, filterMode, sortMode, currentPlayerUsername])

  if (discoveredArtifacts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-gray-400">
        <Trophy className="w-12 h-12 mb-4 text-gray-600" />
        <p className="text-sm font-medium">{t('discoverers.empty')}</p>
        <p className="text-xs text-gray-500 mt-1">{t('discoverers.empty.hint')}</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 bg-white/5 rounded-xl border border-cosmic-border p-1">
          <button
            onClick={() => setFilterMode('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filterMode === 'all'
                ? 'bg-neon-cyan/20 text-neon-cyan'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {t('discoverers.all')}
          </button>
          <button
            onClick={() => setFilterMode('mine')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filterMode === 'mine'
                ? 'bg-neon-cyan/20 text-neon-cyan'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {t('discoverers.mine')}
          </button>
        </div>

        <div className="flex items-center gap-1 ml-auto">
          <Filter className="w-4 h-4 text-gray-500" />
          {(['date', 'tier', 'rarity'] as SortMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setSortMode(mode)}
              className={`px-2 py-1 rounded text-[10px] font-medium transition-all ${
                sortMode === mode
                  ? 'bg-white/10 text-white'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {mode === 'date' ? t('discoverers.sort.date') : mode === 'tier' ? t('discoverers.sort.tier') : t('discoverers.sort.rarity')}
            </button>
          ))}
        </div>
      </div>

      {/* Discovery cards */}
      <div className="space-y-3">
        {discoveredArtifacts.map((artifact) => {
          const rarity = RARITY_STYLES[artifact.rarity] || RARITY_STYLES.common
          const name = artifact.name[language as keyof typeof artifact.name] || artifact.name.ru
          const isMyDiscovery = artifact.discovered_by.includes(currentPlayerUsername)
          const discoveredDate = artifact.discovered_at
            ? new Date(artifact.discovered_at).toLocaleDateString('ru-RU')
            : '—'

          return (
            <motion.div
              key={artifact.slug}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`relative rounded-2xl border ${isMyDiscovery ? 'border-rarity-legendary/60 shadow-glow-legendary' : rarity.border} bg-cosmic-card/50 backdrop-blur-xl overflow-hidden`}
            >
              {isMyDiscovery && (
                <div className="absolute top-2 right-2 z-10">
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-rarity-legendary/20 text-rarity-legendary border border-rarity-legendary/30 font-bold">
                    {t('discoverers.my.badge')}
                  </span>
                </div>
              )}

              <div className="p-4">
                {/* Header: Art + Name */}
                <div className="flex items-center gap-4 mb-3">
                  <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${rarity.badge.split(' ')[0].replace('bg-', 'from-').replace('/20', '/10')} to-cosmic-bg/50 border ${rarity.border} flex items-center justify-center flex-shrink-0`}>
                    <Star className="w-8 h-8 text-white/30" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <h3 className={`text-sm font-bold ${artifact.rarity === 'rare' || artifact.rarity === 'epic' || artifact.rarity === 'legendary' ? 'bg-gradient-to-r from-neon-cyan to-purple-400 bg-clip-text text-transparent' : 'text-white'}`}>
                      {name}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-gray-400 font-medium">
                        T{artifact.tier}
                      </span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${rarity.badge} uppercase`}>
                        {artifact.rarity === 'common' ? t('rarity.common') : artifact.rarity === 'uncommon' ? t('rarity.uncommon') : artifact.rarity === 'rare' ? t('rarity.rare') : artifact.rarity === 'epic' ? t('rarity.epic') : t('rarity.legendary')}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Essence recipe */}
                <div className="mb-3">
                  <p className="text-[10px] uppercase tracking-widest text-gray-500 font-medium mb-2">{t('discoverers.recipe')}</p>
                  <div className="flex flex-wrap gap-2">
                    {artifact.crafting_recipe.map((essenceSlug) => {
                      const essence = essences[essenceSlug]
                      const essenceName = essence
                        ? (essence.name[language as keyof typeof essence.name] || essence.name.ru)
                        : essenceSlug
                      return (
                        <div
                          key={essenceSlug}
                          className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-white/5 border border-white/10"
                        >
                          <Gem className="w-3 h-3 text-neon-purple/50" />
                          <span className="text-[11px] text-gray-300">{essenceName}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Footer: Discoverer + Date */}
                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                  <div className="flex items-center gap-2">
                    <Trophy className="w-3 h-3 text-rarity-legendary/50" />
                    <span className="text-[11px] text-gray-400">
                      {t('discoverers.discovered')}: <span className="text-white font-medium">{artifact.discovered_by[0] || '—'}</span>
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-gray-500" />
                    <span className="text-[10px] text-gray-500">{discoveredDate}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
