import { useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, Zap, Target, Rocket, Wrench } from 'lucide-react'
import { Spaceship } from './Spaceship'
import { StatSlot } from './StatSlot'
import type { ShipConfig } from '../types'
import { useI18n } from '../hooks/useI18n'

const RARITY_COLORS: Record<number, {
  from: string
  to: string
  border: string
  text: string
  glow: string
  badge: string
  glowBg: string
}> = {
  1: {
    from: 'from-gray-500/20',
    to: 'to-gray-600/20',
    border: 'border-gray-500/30',
    text: 'text-gray-400',
    glow: 'shadow-glow-common',
    badge: 'bg-gray-500/20 text-gray-400',
    glowBg: 'bg-gray-400/30',
  },
  2: {
    from: 'from-green-500/20',
    to: 'to-green-600/20',
    border: 'border-green-500/30',
    text: 'text-green-400',
    glow: 'shadow-glow-uncommon',
    badge: 'bg-green-500/20 text-green-400',
    glowBg: 'bg-green-400/30',
  },
  3: {
    from: 'from-blue-500/20',
    to: 'to-blue-600/20',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
    glow: 'shadow-glow-rare',
    badge: 'bg-blue-500/20 text-blue-400',
    glowBg: 'bg-cyan-400/30',
  },
  4: {
    from: 'from-purple-500/20',
    to: 'to-purple-600/20',
    border: 'border-purple-500/30',
    text: 'text-purple-400',
    glow: 'shadow-glow-epic',
    badge: 'bg-purple-500/20 text-purple-400',
    glowBg: 'bg-purple-400/30',
  },
  5: {
    from: 'from-yellow-500/20',
    to: 'to-yellow-600/20',
    border: 'border-yellow-500/30',
    text: 'text-yellow-400',
    glow: 'shadow-glow-legendary',
    badge: 'bg-yellow-500/20 text-yellow-400',
    glowBg: 'bg-yellow-400/30',
  },
}

interface HangarCardProps {
  ship: ShipConfig
  onClick: () => void
  onLaunch: () => void
  isLaunching?: boolean
  stability?: number
  ownedRepairMats?: number
  requiredRepairMats?: number
  onRepair?: () => void
}

export function HangarCard({
  ship,
  onClick,
  onLaunch,
  isLaunching = false,
  stability = 100,
  ownedRepairMats = 0,
  requiredRepairMats = 0,
  onRepair,
}: HangarCardProps) {
  const { t } = useI18n()
  const rarity = RARITY_COLORS[ship.tier] || RARITY_COLORS[1]
  const shipName = ship.name.en
  const [imageFailed, setImageFailed] = useState(false)
  const isDamaged = stability < 100
  const isCritical = stability < 20
  const canRepair = ownedRepairMats >= requiredRepairMats && isDamaged

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="relative w-full"
    >
      <div className={`absolute -inset-1 bg-gradient-to-br ${rarity.from} via-transparent ${rarity.to} rounded-3xl blur-xl`} />

      <div
        className={`relative bg-white/5 backdrop-blur-xl border ${rarity.border} rounded-3xl p-5 overflow-hidden cursor-pointer hover:border-white/20 transition-colors`}
        onClick={onClick}
      >
        <div className={`absolute inset-0 bg-gradient-to-br ${rarity.from} via-transparent ${rarity.to}`} />

        <div className="relative z-10">
          <div className="flex items-center justify-between mb-3">
            <div>
              <motion.h2
                className="text-lg font-bold tracking-wider"
                style={{
                  background: 'linear-gradient(90deg, #06B6D4, #ffffff, #A855F7)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
                animate={{ backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'] }}
                transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
              >
                {shipName}
              </motion.h2>
              <div className="flex items-center gap-2 mt-1">
                  <span className={`text-[10px] uppercase tracking-widest ${rarity.text} font-medium`}>
                    {t('misc.tier')} {ship.tier}
                  </span>
                {ship.is_nft && (
                  <span className="text-[10px] uppercase tracking-widest text-neon-purple font-medium">
                    · NFT
                  </span>
                )}
                {isDamaged ? (
                  <span className="text-[10px] uppercase tracking-widest text-red-400 px-2 py-0.5 rounded-full bg-red-400/20">
                    🔧 {stability}%
                  </span>
                ) : (
                  <span className={`text-[10px] uppercase tracking-widest ${rarity.badge} px-2 py-0.5 rounded-full`}>
                    {t('hangar.ready')}
                  </span>
                )}
              </div>
              <p className={`text-xs mt-1.5 ${rarity.text} italic`}>
                {ship.short_description?.ru || ship.short_description?.en}
              </p>
            </div>
          </div>

          {/* Stability bar */}
          {isDamaged && (
            <div className="mb-3">
              <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
                <span>{t('hangar.stability')}</span>
                <span className={isCritical ? 'text-red-400 font-bold' : 'text-gray-300'}>
                  {stability}% / 100%
                </span>
              </div>
              <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  className={`h-full rounded-full ${isCritical ? 'bg-red-500' : stability < 50 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${stability}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                />
              </div>
              {requiredRepairMats > 0 && (
                <p className="text-[10px] text-gray-500 mt-1">
                  {t('hangar.required')}: {requiredRepairMats}x {t('hangar.repair.kit')} T{ship.tier}
                  {ownedRepairMats >= requiredRepairMats
                    ? ' ✅'
                    : ` (${t('hangar.owned')}: ${ownedRepairMats})`}
                </p>
              )}
            </div>
          )}

          <div className="flex justify-center py-4">
            {ship.art_path && !imageFailed ? (
              <motion.div
                animate={{ y: [0, -12, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                className="relative w-40 h-40"
              >
                <div className={`absolute inset-0 blur-2xl opacity-40 ${rarity.glowBg}`} />
                <img
                  src={ship.art_path}
                  alt={ship.name.ru || ship.name.en}
                  className="relative z-10 w-full h-full object-contain drop-shadow-lg"
                  loading="lazy"
                  onError={(e) => {
                    console.error(`[HangarCard] Не удалось загрузить арт: ${ship.art_path}`)
                    setImageFailed(true)
                  }}
                />
              </motion.div>
            ) : (
              <Spaceship tier={ship.tier} />
            )}
          </div>

          <div className="grid grid-cols-3 gap-3 mt-3 mb-5">
            <StatSlot icon={Shield} label={t('hangar.stability')} value={`${stability}%`} valueColor={isDamaged ? 'text-red-400' : rarity.text} delay={0.1} />
            <StatSlot icon={Zap} label={t('hangar.slots')} value={ship.expedition_slots} valueColor={rarity.text} delay={0.2} />
            <StatSlot icon={Target} label={t('hangar.tier')} value={`T${ship.tier}`} valueColor={rarity.text} delay={0.3} />
          </div>

          {/* Repair button */}
          {isDamaged && (
            <motion.button
              onClick={(e) => {
                e.stopPropagation()
                onRepair?.()
              }}
              disabled={!canRepair}
              className="relative w-full mb-2 group disabled:opacity-40 disabled:cursor-not-allowed"
              whileTap={{ scale: 0.95 }}
            >
              <div
                className="relative px-6 py-2.5 rounded-xl border border-yellow-400/50 backdrop-blur-sm overflow-hidden"
                style={{ background: 'linear-gradient(135deg, rgba(234, 179, 8, 0.15), rgba(245, 158, 11, 0.15))' }}
              >
                <div className="relative flex items-center justify-center gap-2">
                  <Wrench className="w-4 h-4 text-yellow-300" />
                  <span className="text-xs font-bold tracking-widest text-white uppercase">
                    {t('hangar.repair')}
                  </span>
                </div>
              </div>
            </motion.button>
          )}

          <motion.button
            onClick={(e) => {
              e.stopPropagation()
              onLaunch()
            }}
            disabled={isLaunching || isCritical}
            className="relative w-full group disabled:opacity-40 disabled:cursor-not-allowed"
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              className="absolute inset-0 rounded-2xl opacity-60"
              style={{
                background: 'linear-gradient(135deg, #06B6D4, #A855F7, #06B6D4)',
                backgroundSize: '200% 200%',
              }}
              animate={{
                backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                scale: [1, 1.02, 1],
              }}
              transition={{
                backgroundPosition: { duration: 3, repeat: Infinity, ease: 'linear' },
                scale: { duration: 1.5, repeat: Infinity, ease: 'easeInOut' },
              }}
            />

            <motion.div
              className="absolute inset-0 rounded-2xl blur-lg"
              style={{ background: 'linear-gradient(135deg, #06B6D4, #A855F7)' }}
              animate={{ opacity: [0.3, 0.6, 0.3], scale: [0.98, 1.02, 0.98] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
            />

            <div
              className="relative px-6 py-3.5 rounded-2xl border border-cyan-400/50 backdrop-blur-sm overflow-hidden"
              style={{ background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(168, 85, 247, 0.15))' }}
            >
              <motion.div
                className="absolute inset-0 opacity-30"
                style={{ background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)' }}
                animate={{ x: ['-100%', '200%'] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut', repeatDelay: 1 }}
              />

              <div className="relative flex items-center justify-center gap-3">
                <motion.div
                  animate={isLaunching ? { rotate: 360 } : { rotate: [0, -10, 10, 0] }}
                  transition={{ duration: isLaunching ? 1 : 1, repeat: isLaunching ? Infinity : Infinity, ease: 'easeInOut' }}
                >
                  <Rocket className="w-5 h-5 text-cyan-300" />
                </motion.div>
                <span className="text-sm font-bold tracking-widest text-white uppercase">
                  {isLaunching ? t('hangar.launching') : isCritical ? t('hangar.critical') : t('hangar.launch')}
                </span>
              </div>
            </div>
          </motion.button>
        </div>

        <div className={`absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 ${rarity.border} rounded-tl-3xl`} />
        <div className={`absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 ${rarity.border} rounded-br-3xl`} />
      </div>
    </motion.div>
  )
}
