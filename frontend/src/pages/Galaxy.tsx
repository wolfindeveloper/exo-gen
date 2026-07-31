import { useCallback, useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'

import { Skeleton } from '../components/Skeleton'
import { PullToRefresh } from '../components/PullToRefresh'
import { ZoneCard } from '../components/ZoneCard'
import { ZoneModal } from '../components/ZoneModal'
import { fadeIn, scaleIn, staggerContainer } from '../lib/animations'
import { useGameStore } from '../store/game'
import { ZONE_UNLOCK_TABLE } from '../lib/progression'
import type { Zone } from '../types'

const tierLabels = ['', 'T1', 'T2', 'T3', 'T4', 'T5']
const tierColors = ['', 'text-neon-cyan border-neon-cyan/30', 'text-neon-green border-neon-green/30', 'text-neon-purple border-neon-purple/30', 'text-neon-amber border-neon-amber/30', 'text-neon-red border-neon-red/30']
const tierBg = ['', 'bg-neon-cyan/10', 'bg-neon-green/10', 'bg-neon-purple/10', 'bg-neon-amber/10', 'bg-neon-red/10']

export function Galaxy() {
  const zones = useGameStore((s) => s.zonesContent)
  const startExpedition = useGameStore((s) => s.startExpedition)
  const isLoading = useGameStore((s) => s.isLoading)
  const ships = useGameStore((s) => s.ships)
  const loadShips = useGameStore((s) => s.loadShips)
  const loadContent = useGameStore((s) => s.loadContent)
  const user = useGameStore((s) => s.user)
  const playerLevel = user?.level ?? 1
  const [tierFilter, setTierFilter] = useState(1)
  const [zoneModal, setZoneModal] = useState<Zone | null>(null)

  useEffect(() => {
    if (ships.length === 0) loadShips()
  }, [])

  useEffect(() => {
    setZoneModal(null)
  }, [tierFilter])

  const maxTier = 5
  const filteredZones = zones.filter((z) => z.tier === tierFilter)

  const handleStartFromModal = async () => {
    if (!zoneModal) return
    await startExpedition(zoneModal.id)
    setZoneModal(null)
  }

  const handleZoneSelect = (zone: Zone) => {
    setZoneModal(zone)
  }

  const handleCloseModal = () => {
    setZoneModal(null)
  }

  const handleRefresh = useCallback(async () => {
    await loadContent()
  }, [loadContent])

  return (
    <PullToRefresh onRefresh={handleRefresh}>
    <div className="p-4 pb-28">
      <motion.header className="mb-5" variants={fadeIn} initial="hidden" animate="visible">
        <h1 className="font-display text-lg uppercase tracking-[0.2em] text-neon-purple">Галактика</h1>
        <p className="text-xs text-slate-500 mt-1">Нажми на зону для просмотра</p>
      </motion.header>

      <motion.div variants={fadeIn} initial="hidden" animate="visible" className="flex gap-2 mb-4 overflow-x-auto pb-1">
        {Array.from({ length: maxTier }, (_, i) => i + 1).map((tier) => {
          const count = zones.filter((z) => z.tier === tier).length
          const active = tierFilter === tier
          return (
            <motion.button
              key={tier}
              variants={scaleIn}
              onClick={() => setTierFilter(tier)}
              className={`relative px-4 py-2 rounded-xl text-xs font-display uppercase tracking-wider border transition whitespace-nowrap ${
                active ? `${tierColors[tier]} ${tierBg[tier]}` : 'text-slate-500 border-white/10 hover:border-white/20'
              }`}
            >
              <span>{tierLabels[tier]}</span>
              <span className="ml-1.5 opacity-60">{count}</span>
            </motion.button>
          )
        })}
      </motion.div>

      <AnimatePresence mode="wait">
        <motion.div
          key={tierFilter}
          className="flex flex-col gap-3"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          exit={{ opacity: 0, y: -10, transition: { duration: 0.15 } }}
        >
          {!zones.length ? (
            <Skeleton variant="zone" count={5} />
          ) : filteredZones.length === 0 ? (
            <div className="glass-card p-8 text-center">
              <p className="text-slate-500 text-xs">Нет зон этого тира</p>
            </div>
          ) : filteredZones.every((z) => playerLevel < (ZONE_UNLOCK_TABLE[z.tier] ?? 1)) ? (
            (() => {
              const nextUnlock = Object.entries(ZONE_UNLOCK_TABLE)
                .map(([t, req]) => ({ tier: Number(t), required: req }))
                .filter((u) => playerLevel < u.required)
                .sort((a, b) => a.required - b.required)[0]
              const xp = user?.xp ?? 0
              const xpNeeded = nextUnlock ? (nextUnlock.required * 1000) - xp : 0
              const xpPct = nextUnlock ? Math.min(100, Math.round((xp / (nextUnlock.required * 1000)) * 100)) : 0
              return (
                <div className="glass-card p-8 text-center">
                  <div className="text-3xl mb-3 opacity-40">🔒</div>
                  <p className="text-slate-500 text-xs font-display uppercase tracking-wider mb-1">Все зоны закрыты для твоего уровня</p>
                  <p className="text-[11px] text-slate-600 mb-4">Набери {xpNeeded} XP чтобы открыть T{nextUnlock?.tier}</p>
                  <div className="max-w-[200px] mx-auto mb-2">
                    <div className="h-2 bg-black/40 rounded-full overflow-hidden border border-white/10">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-neon-cyan/60 to-neon-purple/60"
                        style={{ width: `${xpPct}%`, boxShadow: '0 0 6px rgba(0,245,255,.3)' }}
                      />
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-600 font-mono">{xp} / {nextUnlock ? nextUnlock.required * 1000 : 0} XP</p>
                </div>
              )
            })()
          ) : (
            filteredZones.map((zone, i) => (
              <ZoneCard key={zone.id} zone={zone} onSelect={() => handleZoneSelect(zone)} index={i} playerLevel={playerLevel} />
            ))
          )}
        </motion.div>
      </AnimatePresence>

      <AnimatePresence>
        {zoneModal && (
          <ZoneModal
            zone={zoneModal}
            onClose={handleCloseModal}
            onStart={handleStartFromModal}
            isLoading={isLoading}
            playerLevel={playerLevel}
          />
        )}
      </AnimatePresence>
    </div>
    </PullToRefresh>
  )
}
