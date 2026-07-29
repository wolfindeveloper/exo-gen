import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { Gem, Package, Rocket, Zap } from 'lucide-react'

import { useGameStore } from '../store/game'

interface BoxItem {
  type: string
  item_id?: string
  pool?: string[]
  quantity?: number
  name?: string | null
  image_url?: string | null
}

interface BoxData {
  guaranteed: BoxItem[]
  random: BoxItem[]
}

function ItemIcon({ item, className }: { item: BoxItem; className?: string }) {
  if (item.image_url) {
    return (
      <img src={item.image_url} alt="" className={`w-5 h-5 object-contain ${className ?? ''}`} />
    )
  }
  if (item.type === 'xgen') return <Gem className={`w-4 h-4 text-amber-400 ${className ?? ''}`} />
  if (item.type === 'xp') return <Zap className={`w-4 h-4 text-yellow-400 ${className ?? ''}`} />
  if (item.type === 'ship') return <Rocket className={`w-4 h-4 text-cyan-400 ${className ?? ''}`} />
  return <Package className={`w-4 h-4 text-slate-400 ${className ?? ''}`} />
}

export function BoxReveal() {
  const rawRewards = useGameStore((s) => s.boxRewards)
  const clearBoxRewards = useGameStore((s) => s.clearBoxRewards)
  const shipsContent = useGameStore((s) => s.shipsContent)
  const resourcesContent = useGameStore((s) => s.resourcesContent)
  const artifactsContent = useGameStore((s) => s.artifactsContent)

  const [phase, setPhase] = useState<'idle' | 'opening' | 'rewards' | 'done'>('idle')
  const [pickedShip, setPickedShip] = useState<string | null>(null)

  const boxRewards = rawRewards as BoxData | null

  useEffect(() => {
    if (!boxRewards) {
      setPhase('idle')
      return
    }
    setPhase('opening')

    const shipEntry = boxRewards.guaranteed.find((r) => r.type === 'ship')
    let chosenShip = ''
    if (shipEntry?.pool?.length) {
      chosenShip = shipEntry.pool[Math.floor(Math.random() * shipEntry.pool.length)]
    }
    setPickedShip(chosenShip)

    const t = setTimeout(() => setPhase('rewards'), 1200)
    return () => clearTimeout(t)
  }, [rawRewards])

  if (!boxRewards || phase === 'idle') return null

  const handleClose = () => {
    setPhase('done')
    setTimeout(() => clearBoxRewards(), 300)
  }

  const shipName = pickedShip
    ? shipsContent.find((s) => s.id === pickedShip)?.name_key || pickedShip
    : ''

  function getItemLabel(item: BoxItem): string {
    return item.name || resourcesContent.find((e) => e.id === item.item_id)?.name_key || artifactsContent.find((a) => a.id === item.item_id)?.name_key || item.item_id || 'Предмет'
  }

  return (
    <AnimatePresence>
      {phase !== 'done' && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={handleClose}
        >
          {phase === 'opening' && (
            <motion.div
              className="text-center"
              initial={{ scale: 0.3, rotate: -10 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: 'spring', damping: 12 }}
            >
              <div className="text-7xl mb-4">🎁</div>
              <motion.div
                className="text-5xl mb-3"
                animate={{ rotate: [0, 15, -15, 0] }}
                transition={{ repeat: Infinity, duration: 0.6 }}
              >
                <Package className="w-12 h-12 text-neon-cyan" />
              </motion.div>
              <p className="font-display text-lg text-neon-cyan uppercase tracking-widest">
                Открываем бокс...
              </p>
            </motion.div>
          )}

          {phase === 'rewards' && (
            <motion.div
              className="w-full max-w-sm mx-4"
              initial={{ scale: 0.8, y: 40 }}
              animate={{ scale: 1, y: 0 }}
              transition={{ type: 'spring', damping: 14 }}
            >
              <div className="glass-card p-5 text-center mb-4">
                <div className="text-5xl mb-3">🎉</div>
                <h2 className="font-display text-lg text-neon-cyan uppercase tracking-widest mb-1">
                  Поздравляем!
                </h2>
                <p className="text-xs text-slate-500">Вы получили стартовый набор</p>
              </div>

              <div className="glass-card p-4 mb-3">
                <p className="text-[10px] font-display uppercase tracking-wider text-slate-500 mb-2">
                  Гарантировано
                </p>
                <div className="space-y-2">
                  {boxRewards.guaranteed.map((r, i) => (
                    <RewardRow key={i} icon={<ItemIcon item={r} />} label={r.type === 'ship' ? (shipName || 'Корабль') : (r.type === 'xgen' ? 'XGEN' : r.type === 'xp' ? 'XP' : getItemLabel(r))} qty={r.quantity} />
                  ))}
                </div>
              </div>

              {boxRewards.random.length > 0 && (
                <div className="glass-card p-4 mb-4">
                  <p className="text-[10px] font-display uppercase tracking-wider text-slate-500 mb-2">
                    Случайные находки
                  </p>
                  <div className="space-y-2">
                    {boxRewards.random.map((r, i) => (
                      <RewardRow key={i} icon={<ItemIcon item={r} />} label={getItemLabel(r)} qty={r.quantity} />
                    ))}
                  </div>
                </div>
              )}

              <button
                className="w-full py-3 rounded-xl bg-neon-cyan/20 border border-neon-cyan/40 text-neon-cyan font-display text-sm uppercase tracking-widest hover:bg-neon-cyan/30 transition-all"
                onClick={handleClose}
              >
                В путь!
              </button>
            </motion.div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

function RewardRow({ icon, label, qty }: { icon: React.ReactNode; label: string; qty?: number }) {
  return (
    <div className="flex items-center justify-between bg-space-600/50 rounded-lg px-3 py-2">
      <div className="flex items-center gap-2">
        {icon}
        <span className="text-sm text-slate-200">{label}</span>
      </div>
      {qty !== undefined && <span className="font-display text-neon-cyan">x{qty}</span>}
    </div>
  )
}
