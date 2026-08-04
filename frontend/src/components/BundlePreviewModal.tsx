import { motion, AnimatePresence } from 'motion/react'
import { X, Package, Diamond, FlaskConical, Key, Box } from 'lucide-react'
import type { BundleItemInfo } from '../types'

const rarityConfig: Record<string, { color: string; label: string; border: string; bg: string }> = {
  common:    { color: 'text-slate-400',   label: '\u041e\u0431\u044b\u0447\u043d\u044b\u0439',     border: 'border-slate-500/30',  bg: 'bg-slate-500/10' },
  uncommon:  { color: 'text-green-400',   label: '\u041d\u0435\u043e\u0431\u044b\u0447\u043d\u044b\u0439',   border: 'border-green-500/30',  bg: 'bg-green-500/10' },
  rare:      { color: 'text-blue-400',    label: '\u0420\u0435\u0434\u043a\u0438\u0439',      border: 'border-blue-500/30',   bg: 'bg-blue-500/10' },
  epic:      { color: 'text-purple-400',  label: '\u042d\u043f\u0438\u0447\u0435\u0441\u043a\u0438\u0439',   border: 'border-purple-500/30', bg: 'bg-purple-500/10' },
  legendary: { color: 'text-amber-400',   label: '\u041b\u0435\u0433\u0435\u043d\u0434\u0430\u0440\u043d\u044b\u0439', border: 'border-amber-500/30',  bg: 'bg-amber-500/10' },
}

const typeIcons: Record<string, typeof Package> = {
  consumable: FlaskConical,
  artifact: Diamond,
  key_item: Key,
  loot_box: Box,
  material: Package,
}

const typeLabels: Record<string, string> = {
  consumable: '\u0420\u0430\u0441\u0445\u043e\u0434\u043d\u0438\u043a',
  artifact: '\u0410\u0440\u0442\u0435\u0444\u0430\u043a\u0442',
  key_item: '\u041a\u043b\u044e\u0447\u0435\u0432\u043e\u0439 \u043f\u0440\u0435\u0434\u043c\u0435\u0442',
  loot_box: '\u041a\u043e\u043d\u0442\u0435\u0439\u043d\u0435\u0440',
  material: '\u041c\u0430\u0442\u0435\u0440\u0438\u0430\u043b',
}

interface BundlePreviewModalProps {
  open: boolean
  bundleName: string
  items: BundleItemInfo[]
  onClose: () => void
}

export default function BundlePreviewModal({ open, bundleName, items, onClose }: BundlePreviewModalProps) {
  if (!open) return null

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[80] flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
        <motion.div
          className="relative w-full max-w-md bg-space-900 border border-amber-500/20 rounded-2xl shadow-2xl overflow-hidden"
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
        >
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Package size={18} className="text-amber-400" />
              <h3 className="font-display text-sm text-amber-400 uppercase tracking-wider">
                {'\u0421\u043e\u0434\u0435\u0440\u0436\u0438\u043c\u043e\u0435 \u043d\u0430\u0431\u043e\u0440\u0430'}
              </h3>
            </div>
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-full bg-white/5 flex items-center justify-center text-slate-400 hover:text-white transition-colors"
            >
              <X size={14} />
            </button>
          </div>

          <div className="px-5 pt-4 pb-2">
            <p className="font-display text-xs text-slate-300 uppercase tracking-wider">
              {bundleName}
            </p>
            <p className="text-[10px] text-slate-500 mt-1">
              {items.length} {items.length === 1 ? '\u043f\u0440\u0435\u0434\u043c\u0435\u0442' : items.length < 5 ? '\u043f\u0440\u0435\u0434\u043c\u0435\u0442\u0430' : '\u043f\u0440\u0435\u0434\u043c\u0435\u0442\u043e\u0432'} {'\u0432 \u043d\u0430\u0431\u043e\u0440\u0435'}
            </p>
          </div>

          <div className="px-5 pb-5 space-y-2 max-h-[50vh] overflow-y-auto">
            {items.map((item, i) => {
              const rarity = rarityConfig[item.rarity] || rarityConfig.common
              const TypeIcon = typeIcons[item.type] || Package
              const typeLabel = typeLabels[item.type] || item.type

              return (
                <motion.div
                  key={item.item_id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={`flex items-center gap-3 p-3 rounded-xl border ${rarity.border} ${rarity.bg}`}
                >
                  <div className={`shrink-0 w-10 h-10 rounded-lg flex items-center justify-center border ${rarity.border} bg-black/30 overflow-hidden`}>
                    {item.image_url ? (
                      <img src={item.image_url} alt={item.name} className="w-full h-full object-cover" />
                    ) : (
                      <TypeIcon size={18} className={rarity.color} />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-xs text-slate-200 font-medium truncate">
                        {item.name}
                      </span>
                      {item.quantity > 1 && (
                        <span className="text-[9px] font-mono text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">
                          \u00d7{item.quantity}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className={`text-[8px] font-display uppercase tracking-wider px-1.5 py-0.5 rounded border ${rarity.border} ${rarity.color} ${rarity.bg}`}>
                        {rarity.label}
                      </span>
                      <span className="text-[8px] text-slate-500">
                        {typeLabel}
                      </span>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>

          <div className="px-5 pb-5">
            <button
              onClick={onClose}
              className="w-full py-2.5 rounded-xl bg-white/5 text-slate-300 text-[10px] font-display uppercase tracking-wider border border-white/10 hover:bg-white/10 transition-colors"
            >
              {'\u0417\u0430\u043a\u0440\u044b\u0442\u044c'}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
