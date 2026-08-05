import { type ReactNode, useEffect } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { hapticImpact } from '../lib/telegram'

interface ConfirmDialogProps {
  open: boolean
  title: string
  description: ReactNode
  confirmLabel: string
  cancelLabel?: string
  destructive?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel,
  cancelLabel = 'Отмена',
  destructive = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  useEffect(() => {
    if (open) hapticImpact('heavy')
  }, [open])

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[80] flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onCancel} />
          <motion.div
            className="relative w-full max-w-sm glass-card p-5 shadow-2xl border border-white/10 max-h-[80vh] overflow-y-auto"
            initial={{ scale: 0.9, opacity: 0, y: 12 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 8 }}
            transition={{ type: 'spring', stiffness: 400, damping: 28, mass: 0.8 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-sm font-display uppercase tracking-wider text-slate-200 mb-2">
              {title}
            </h3>
            <div className="text-[11px] text-slate-400 leading-relaxed mb-5">
              {description}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  hapticImpact('light')
                  onCancel()
                }}
                className="flex-1 py-2.5 rounded-xl bg-white/5 border border-white/10 text-[10px] font-display uppercase tracking-wider text-slate-400 hover:bg-white/10 transition-colors"
              >
                {cancelLabel}
              </button>
              <button
                onClick={() => {
                  hapticImpact('medium')
                  onConfirm()
                }}
                className={`flex-1 py-2.5 rounded-xl text-[10px] font-display uppercase tracking-wider transition-colors border ${
                  destructive
                    ? 'bg-red-500/15 border-red-500/30 text-red-400 hover:bg-red-500/25'
                    : 'bg-neon-cyan/15 border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/25'
                }`}
              >
                {confirmLabel}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
