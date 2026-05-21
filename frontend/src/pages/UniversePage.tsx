import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BookOpen } from 'lucide-react'
import { useConfigStore } from '../store/useConfigStore'
import { usePlayerStore } from '../store/usePlayerStore'
import { Starfield } from '../components/Starfield'
import SubMenu from '../components/layout/SubMenu'
import WalletConnect from '../components/wallet/WalletConnect'
import {
  SectorAccordion,
  CosmicMap,
  ZoneDetailModal,
} from '../components/galaxy'
import type { GalaxyZoneConfig } from '../types'
import { useI18n } from '../hooks/useI18n'

const UniversePage = () => {
  const { zones, isLoading } = useConfigStore()
  const { t, language } = useI18n()
  const [activeTab, setActiveTab] = useState('sectors')
  const [selectedZone, setSelectedZone] = useState<GalaxyZoneConfig | null>(null)

  const universeTabs = [
    { id: 'sectors', label: t('tab.sectors') },
    { id: 'map', label: t('tab.map') },
    { id: 'lore', label: t('tab.lore') },
  ]

  const handleZoneClick = useCallback((slug: string) => {
    const zone = zones[slug]
    if (zone) setSelectedZone(zone)
  }, [zones])

  const handleCloseModal = useCallback(() => {
    setSelectedZone(null)
  }, [])

  const zoneList = Object.values(zones).filter(
    (z): z is GalaxyZoneConfig => !!z && !!z.slug
  )

  return (
    <div className="relative min-h-screen pt-28 pb-24 px-3">
      <Starfield />

      <div className="relative z-10 max-w-lg mx-auto">
        <WalletConnect />
        <SubMenu tabs={universeTabs} activeTab={activeTab} onChange={setActiveTab} />

        <AnimatePresence mode="wait">
          {/* SECTORS Tab */}
          {activeTab === 'sectors' && (
            <motion.div
              key="sectors"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
            >
              {isLoading || zoneList.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 text-gray-400">
                  <span className="text-4xl mb-4">🌌</span>
                  <p className="text-sm">{isLoading ? t('universe.loading.sectors') : t('universe.no.sectors')}</p>
                </div>
              ) : (
                <SectorAccordion
                  zones={zoneList}
                  onZoneClick={handleZoneClick}
                  language={language}
                />
              )}
            </motion.div>
          )}

          {/* MAP Tab */}
          {activeTab === 'map' && (
            <motion.div
              key="map"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="mt-4"
            >
              {isLoading || zoneList.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 text-gray-400 bg-white/5 backdrop-blur-xl border border-cosmic-border rounded-2xl">
                  <span className="text-4xl mb-4">🗺️</span>
                  <p className="text-sm">{isLoading ? t('universe.loading.map') : t('universe.no.map')}</p>
                </div>
              ) : (
                <CosmicMap zones={zoneList} onZoneClick={handleZoneClick} />
              )}
            </motion.div>
          )}

          {/* LORE Tab */}
          {activeTab === 'lore' && (
            <motion.div
              key="lore"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="mt-4"
            >
              <div className="bg-white/5 backdrop-blur-xl border border-cosmic-border rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <BookOpen className="w-5 h-5 text-neon-purple" />
                  <h3 className="text-sm font-bold text-white">{t('universe.lore.title')}</h3>
                </div>
                <div className="space-y-4 text-sm text-gray-300 leading-relaxed">
                  <p>
                    {t('universe.lore.p1')}
                  </p>
                  <p>
                    {t('universe.lore.p2')}
                  </p>
                  <p>
                    {t('universe.lore.p3')}
                  </p>
                </div>
                <div className="mt-6 pt-4 border-t border-cosmic-border">
                  <p className="text-xs text-gray-500 text-center">{t('universe.lore.footer')}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Zone Detail Modal */}
      <ZoneDetailModal
        zone={selectedZone}
        onClose={handleCloseModal}
        language={language}
      />
    </div>
  )
}

export default UniversePage
