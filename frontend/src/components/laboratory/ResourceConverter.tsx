/**
 * Компонент конвертации ремнаборов: 1x T(N) → 2x T(N-1)
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowDown, Wrench, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'
import { post } from '../../lib/api'
import { usePlayerStore } from '../../store/usePlayerStore'
import { useI18n } from '../../hooks/useI18n'

interface ResourceConverterProps {
  repairMats: Record<string, number>
  onConvertSuccess?: () => void
}

export function ResourceConverter({ repairMats, onConvertSuccess }: ResourceConverterProps) {
  const { t } = useI18n()
  const { convertMats } = usePlayerStore()
  const [sourceTier, setSourceTier] = useState(2)
  const [amount, setAmount] = useState(1)

  const sourceSlug = `repair_matter_t${sourceTier}`
  const targetSlug = `repair_matter_t${sourceTier - 1}`
  const targetAmount = amount * 2
  const owned = repairMats[sourceSlug] || 0
  const canConvert = owned >= amount && sourceTier >= 2

  const handleConvert = async () => {
    if (!canConvert) return

    try {
      await post('/resources/convert', {
        source_tier: sourceTier,
        amount,
      })
      toast.success(`${t('converter.toast.success')}: ${amount}x T${sourceTier} → ${targetAmount}x T${sourceTier - 1}`)
      onConvertSuccess?.()
    } catch (err) {
      console.error('Convert failed:', err)
      toast.error(t('converter.toast.error'))
    }
  }

  const tiers = [2, 3, 4, 5].filter((t) => {
    const slug = `repair_matter_t${t}`
    return (repairMats[slug] || 0) > 0
  })

  if (tiers.length === 0) {
    return (
      <div className="px-4 py-8 text-center">
        <Wrench className="w-8 h-8 text-gray-600 mx-auto mb-2" />
        <p className="text-xs text-gray-500">
          {t('converter.empty')}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Source tier selector */}
      <div>
        <label className="text-xs text-gray-400 mb-2 block">
          {t('converter.source')}
        </label>
        <div className="flex gap-2">
          {[2, 3, 4, 5].map((tier) => {
            const slug = `repair_matter_t${tier}`
            const hasMats = (repairMats[slug] || 0) > 0
            const isSelected = sourceTier === tier
            return (
              <button
                key={tier}
                disabled={!hasMats}
                onClick={() => setSourceTier(tier)}
                className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
                  isSelected
                    ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50'
                    : hasMats
                    ? 'bg-white/5 text-gray-400 border border-white/10 hover:border-white/20'
                    : 'bg-white/5 text-gray-600 border border-white/10 cursor-not-allowed opacity-50'
                }`}
              >
                T{tier}
                <span className="block text-[10px] text-gray-500">
                  {repairMats[slug] || 0}x
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Amount input */}
      <div>
        <label className="text-xs text-gray-400 mb-2 block">
          {t('converter.amount')}
        </label>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setAmount(Math.max(1, amount - 1))}
            className="w-8 h-8 rounded-lg bg-white/10 text-white font-bold hover:bg-white/20"
          >
            −
          </button>
          <input
            type="number"
            min={1}
            max={owned}
            value={amount}
            onChange={(e) => setAmount(Math.max(1, Math.min(owned, parseInt(e.target.value) || 1)))}
            className="flex-1 h-8 rounded-lg bg-white/5 border border-white/10 text-center text-white text-sm"
          />
          <button
            onClick={() => setAmount(Math.min(owned, amount + 1))}
            className="w-8 h-8 rounded-lg bg-white/10 text-white font-bold hover:bg-white/20"
          >
            +
          </button>
        </div>
        <p className="text-[10px] text-gray-500 mt-1">
          {t('converter.available')}: {owned}x
        </p>
      </div>

      {/* Conversion preview */}
      <div className="px-4 py-3 rounded-xl bg-white/5 border border-white/10">
        <div className="flex items-center justify-center gap-3">
          <span className="text-sm font-bold text-yellow-400">
            {amount}x T{sourceTier}
          </span>
          <ArrowDown className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-bold text-green-400">
            {targetAmount}x T{sourceTier - 1}
          </span>
        </div>
      </div>

      {/* Warning */}
      {!canConvert && (
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/20">
          <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span className="text-xs text-red-400">
            {t('converter.insufficient')} T{sourceTier}
          </span>
        </div>
      )}

      {/* Convert button */}
      <motion.button
        onClick={handleConvert}
        disabled={!canConvert}
        className="relative w-full py-3 rounded-xl font-bold text-white text-sm overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30"
        whileTap={{ scale: 0.98 }}
      >
          {t('converter.convert')}
      </motion.button>
    </div>
  )
}
