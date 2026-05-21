import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Fuel, Gem, Star, Wrench } from 'lucide-react'
import { Fuel as FuelType, Essence, Artifact, RepairMat, ResourceItem } from '../../types'
import { ResourceItemRow } from './ResourceItemRow'
import { ResourceCard } from './ResourceCard'
import { useI18n } from '../../hooks/useI18n'

interface ResourcesAccordionProps {
  fuels: Record<string, FuelType>
  essences: Record<string, Essence>
  artifacts: Record<string, Artifact>
  repairMats: Record<string, RepairMat>
  onItemSelect: (item: ResourceItem) => void
  language?: 'ru' | 'en' | 'la'
}

export function ResourcesAccordion({ fuels, essences, artifacts, repairMats, onItemSelect, language = 'ru' }: ResourcesAccordionProps) {
  const { t } = useI18n()
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    fuels: true,
    essences: false,
    artifacts: false,
  })

  const toggleSection = (key: string) => {
    setExpandedSections((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const sections = [
    { key: 'fuels', label: t('resources.fuel'), icon: Fuel },
    { key: 'repair_mats', label: t('resources.repair'), icon: Wrench },
    { key: 'essences', label: t('resources.essences'), icon: Gem },
    { key: 'artifacts', label: t('resources.artifacts'), icon: Star },
  ] as const

  const fuelList = Object.values(fuels).sort((a, b) => a.tier - b.tier)
  const repairMatList = Object.values(repairMats).sort((a, b) => a.tier - b.tier)
  const essenceList = Object.values(essences).sort((a, b) => a.tier - b.tier)
  const artifactList = Object.values(artifacts).sort((a, b) => a.tier - b.tier)

  const sectionData: Record<string, { items: ResourceItem[]; renderItem: (item: ResourceItem) => React.ReactNode }> = {
    fuels: {
      items: fuelList,
      renderItem: (item) => (
        <ResourceItemRow
          key={item.slug}
          item={item as FuelType}
          onClick={() => onItemSelect(item)}
          language={language}
        />
      ),
    },
    repair_mats: {
      items: repairMatList,
      renderItem: (item) => (
        <ResourceItemRow
          key={item.slug}
          item={item}
          onClick={() => onItemSelect(item)}
          language={language}
        />
      ),
    },
    essences: {
      items: essenceList,
      renderItem: (item) => (
        <ResourceCard
          key={item.slug}
          item={item as Essence}
          onClick={() => onItemSelect(item)}
          language={language}
        />
      ),
    },
    artifacts: {
      items: artifactList,
      renderItem: (item) => (
        <ResourceCard
          key={item.slug}
          item={item as Artifact}
          onClick={() => onItemSelect(item)}
          language={language}
        />
      ),
    },
  }

  return (
    <div className="space-y-3 mt-4">
      {sections.map(({ key, label, icon: Icon }) => {
        const isExpanded = expandedSections[key]
        const data = sectionData[key]
        const count = data.items.length

        return (
          <div key={key} className="rounded-2xl border border-cosmic-border bg-cosmic-card/50 overflow-hidden">
            {/* Header */}
            <button
              onClick={() => toggleSection(key)}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors"
              aria-expanded={isExpanded}
              aria-label={label}
            >
              <div className="flex items-center gap-3">
                <Icon className="w-5 h-5 text-neon-cyan" />
                <span className="text-sm font-bold text-white">{label}</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-gray-400 font-medium">
                  {count}
                </span>
              </div>
              <motion.div
                animate={{ rotate: isExpanded ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                <ChevronDown className="w-5 h-5 text-gray-400" />
              </motion.div>
            </button>

            {/* Content */}
            <AnimatePresence initial={false}>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                >
                  <div className={`px-4 pb-4 ${key === 'fuels' ? 'space-y-2' : 'grid grid-cols-1 gap-3'}`}>
                    {count === 0 ? (
                      <p className="text-xs text-gray-500 text-center py-4">{t('resources.empty')}</p>
                    ) : (
                      data.items.map((item) => data.renderItem(item))
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )
      })}
    </div>
  )
}
