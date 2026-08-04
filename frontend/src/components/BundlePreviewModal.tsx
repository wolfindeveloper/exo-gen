import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { X, Package, Diamond, FlaskConical, Key, Box } from 'lucide-react'
import type { BundleItemInfo } from '../types'

const rarityConfig: Record<string, { color: string; text: string; border: string; bg: string }> = {
  common:    { color: 'text-slate-400',   text: 'text-slate-400',   border: 'border-slate-500/30',  bg: 'bg-slate-500/10' },
  uncommon:  { color: 'text-green-400',   text: 'text-green-400',   border: 'border-green-500/30',  bg: 'bg-green-500/10' },
  rare:      { color: 'text-blue-400',    text: 'text-blue-400',    border: 'border-blue-500/30',   bg: 'bg-blue-500/10' },
  epic:      { color: 'text-purple-400',  text: 'text-purple-400',  border: 'border-purple-500/30', bg: 'bg-purple-500/10' },
  legendary: { color: 'text-amber-400',   text: 'text-amber-400',   border: 'border-amber-500/30',  bg: 'bg-amber-500/10' },
}

const rarityLabels: Record<string, string> = {
  common: 'Обычный',
  uncommon: 'Необычный',
  rare: 'Редкий',
  epic: 'Эпический',
  legendary: 'Легендарный',
}

const typeIcons: Record<string, typeof Package> = {
  consumable: FlaskConical,
  artifact: Diamond,
  key_item: Key,
  loot_box: Box,
  material: Package,
}

const typeLabels: Record<string, string> = {
  consumable: 'Расходники',
  artifact: 'Артефакты',
  key_item: 'Ключевой предмет',
  loot_box: 'Контейнер',
  material: 'Материал',
}

interface BundlePreviewModalProps {
  open: boolean
  bundleName: string
  bundleDescription?: string
  items: BundleItemInfo[]
  onClose: () => void
}

export default function BundlePreviewModal({ open, bundleName, bundleDescription, items, onClose }: BundlePreviewModalProps) {
  const [selectedItem, setSelectedItem] = useState<BundleItemInfo | null>(null)

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
          {/* Header — only bundle name + close */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
            <div>
              <p className="font-display text-sm text-amber-400 uppercase tracking-wider">
                {bundleName}
              </p>
              {bundleDescription && (
                <p className="text-[10px] text-slate-500 mt-1 leading-relaxed max-w-[280px]">
                  {bundleDescription}
                </p>
              )}
            </div>
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-full bg-white/5 flex items-center justify-center text-slate-400 hover:text-white transition-colors shrink-0 ml-3"
            >
              <X size={14} />
            </button>
          </div>

          {/* Items count */}
          <div className="px-5 pt-3 pb-1">
            <p className="text-[10px] text-slate-600">
              {items.length} {items.length === 1 ? 'предмет' : items.length < 5 ? 'предмета' : 'предметов'} в наборе
            </p>
          </div>

          {/* Items list */}
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
                  {/* Clickable icon */}
                  <button
                    onClick={() => setSelectedItem(item)}
                    className={`shrink-0 w-10 h-10 rounded-lg flex items-center justify-center border ${rarity.border} bg-black/30 overflow-hidden hover:ring-2 hover:ring-amber-500/40 transition-all cursor-pointer`}
                  >
                    {item.image_url ? (
                      <img src={item.image_url} alt={item.name} className="w-full h-full object-cover" />
                    ) : (
                      <TypeIcon size={18} className={rarity.color} />
                    )}
                  </button>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-xs text-slate-200 font-medium truncate">
                        {item.name}
                      </span>
                      {item.quantity > 1 && (
                        <span className="text-[9px] font-mono text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">
                          ×{item.quantity}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className={`text-[8px] font-display uppercase tracking-wider px-1.5 py-0.5 rounded border ${rarity.border} ${rarity.color} ${rarity.bg}`}>
                        {rarityLabels[item.rarity] || item.rarity}
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

          {/* Footer */}
          <div className="px-5 pb-5">
            <button
              onClick={onClose}
              className="w-full py-2.5 rounded-xl bg-white/5 text-slate-300 text-[10px] font-display uppercase tracking-wider border border-white/10 hover:bg-white/10 transition-colors"
            >
              Закрыть
            </button>
          </div>
        </motion.div>

        {/* Item detail popup */}
        <AnimatePresence>
          {selectedItem && (
            <ItemDetailPopup item={selectedItem} onClose={() => setSelectedItem(null)} />
          )}
        </AnimatePresence>
      </motion.div>
    </AnimatePresence>
  )
}

function ItemDetailPopup({ item, onClose }: { item: BundleItemInfo; onClose: () => void }) {
  const rarity = rarityConfig[item.rarity] || rarityConfig.common
  const TypeIcon = typeIcons[item.type] || Package
  const typeLabel = typeLabels[item.type] || item.type

  return (
    <motion.div
      className="fixed inset-0 z-[90] flex items-end sm:items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <motion.div
        className="relative w-full sm:max-w-md bg-space-900 border border-white/10 rounded-t-2xl sm:rounded-2xl shadow-2xl overflow-y-auto max-h-[80vh]"
        initial={{ y: '100%', opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: '30%', opacity: 0 }}
        transition={{ type: 'spring', stiffness: 400, damping: 35, mass: 0.9 }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 z-10 w-8 h-8 rounded-full bg-black/40 backdrop-blur flex items-center justify-center text-white/70 hover:text-white transition-colors"
        >
          ✕
        </button>

        {/* Icon + name header */}
        <div className={`p-6 ${rarity.bg}`}>
          <div className="flex items-center gap-4">
            <div className="shrink-0 w-16 h-16 rounded-xl border border-white/10 bg-black/30 flex items-center justify-center overflow-hidden">
              {item.image_url ? (
                <img src={item.image_url} alt={item.name} className="w-full h-full object-contain" />
              ) : (
                <TypeIcon size={32} className={rarity.color} />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="font-display text-base uppercase tracking-[0.1em] text-slate-200">{item.name}</h2>
              <div className="flex items-center gap-2 mt-1.5">
                <span className={`text-[10px] font-display uppercase tracking-wider px-2 py-0.5 rounded border ${rarity.border} ${rarity.color} ${rarity.bg}`}>
                  {rarityLabels[item.rarity] || item.rarity}
                </span>
                <span className="text-xs text-slate-500">
                  {typeLabel}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Details */}
        <div className="p-5 space-y-5 pb-24">
          {item.description && (
            <div>
              <h4 className="text-[10px] font-display uppercase tracking-wider text-slate-500 mb-2">Описание</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{item.description}</p>
            </div>
          )}

          <div>
            <h4 className="text-[10px] font-display uppercase tracking-wider text-slate-500 mb-2">Данные</h4>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Количество в наборе</span>
                <span className={`font-mono ${rarity.color}`}>{item.quantity} ед.</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Тип</span>
                <span className="text-slate-300">{typeLabel}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Редкость</span>
                <span className={rarity.color}>{rarityLabels[item.rarity] || item.rarity}</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
