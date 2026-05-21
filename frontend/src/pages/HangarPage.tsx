import { useState, useCallback } from 'react'
import { useConfigStore } from '../store/useConfigStore'
import { usePlayerStore } from '../store/usePlayerStore'
import { startExpedition } from '../lib/api-helpers'
import { useToast, ToastContainer } from '../components/Toast'
import { HangarCard } from '../components/HangarCard'
import { Starfield } from '../components/Starfield'
import SubMenu from '../components/layout/SubMenu'
import ShipModal from '../components/modals/ShipModal'
import { ResourcesAccordion } from '../components/hangar/ResourcesAccordion'
import { ResourceDetailModal } from '../components/hangar/ResourceDetailModal'
import WalletConnect from '../components/wallet/WalletConnect'
import type { ShipConfig, ResourceItem } from '../types'
import { useI18n } from '../hooks/useI18n'

const HangarPage = () => {
  const { ships, fuels, essences, artifacts, repairMats } = useConfigStore()
  const { player, updateBalance, language } = usePlayerStore()
  const { t } = useI18n()
  const { toasts, addToast, removeToast } = useToast()
  const [activeTab, setActiveTab] = useState('ships')
  const [selectedShip, setSelectedShip] = useState<ShipConfig | null>(null)
  const [selectedResource, setSelectedResource] = useState<ResourceItem | null>(null)
  const [launching, setLaunching] = useState<string | null>(null)

  const hangarTabs = [
    { id: 'ships', label: t('tab.ships') },
    { id: 'resources', label: t('tab.resources') },
  ]

  const handleShipClick = useCallback((slug: string) => {
    const ship = ships[slug]
    if (ship) setSelectedShip(ship)
  }, [ships])

  const handleLaunch = useCallback(async (slug: string) => {
    const ship = ships[slug]
    if (!ship) return

    setLaunching(slug)
    try {
      const fuelSlug = ship.tier === 1 ? 'fuel_t1_mangan_hydride' : `fuel_t${ship.tier}_deuterium_x`
      await startExpedition(slug, ship.tier, fuelSlug, 'stable')
      addToast(t('toast.launched'), 'success')
      updateBalance(-50)
    } catch (err) {
      console.error('Expedition start failed:', err)
      addToast(t('toast.no.fuel'), 'error')
    } finally {
      setLaunching(null)
    }
  }, [ships, addToast, updateBalance])

  const handleCloseModal = useCallback(() => {
    setSelectedShip(null)
  }, [])

  const shipList = Object.values(ships)

  // Диагностика: проверяем что art_path загружен для каждого корабля
  if (shipList.length > 0) {
    shipList.forEach((ship) => {
      console.log(`[Hangar] Ship ${ship.name.en}: art_path = ${ship.art_path || '(нет)'}`)
    })
  }

  const handleResourceSelect = useCallback((item: ResourceItem) => {
    setSelectedResource(item)
  }, [])

  const handleCloseResourceModal = useCallback(() => {
    setSelectedResource(null)
  }, [])

  return (
    <div className="relative min-h-screen pt-28 pb-24 px-3">
      <Starfield />
      <ToastContainer toasts={toasts} removeToast={removeToast} />

      <div className="relative z-10 max-w-lg mx-auto">
        <WalletConnect />
        <SubMenu tabs={hangarTabs} activeTab={activeTab} onChange={setActiveTab} />

        {activeTab === 'ships' && (
          <div className="flex flex-col gap-4 mt-4">
            {shipList.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-gray-400">
                <span className="text-4xl mb-4">🚀</span>
                <p className="text-sm">{t('hangar.loading')}</p>
              </div>
            ) : (
              shipList.map((ship) => (
                <HangarCard
                  key={ship.slug}
                  ship={ship}
                  onClick={() => handleShipClick(ship.slug)}
                  onLaunch={() => handleLaunch(ship.slug)}
                  isLaunching={launching === ship.slug}
                />
              ))
            )}
          </div>
        )}

        {activeTab === 'resources' && (
          <ResourcesAccordion
            fuels={fuels}
            essences={essences}
            artifacts={artifacts}
            repairMats={repairMats}
            onItemSelect={handleResourceSelect}
            language={language}
          />
        )}
      </div>

      {selectedShip && (
        <ShipModal ship={selectedShip} onClose={handleCloseModal} language={language} />
      )}

      {selectedResource && (
        <ResourceDetailModal
          item={selectedResource}
          onClose={handleCloseResourceModal}
          language={language}
        />
      )}
    </div>
  )
}

export default HangarPage
