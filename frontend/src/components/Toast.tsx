import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export type ToastType = 'success' | 'error' | 'info'

interface Toast {
  id: number
  message: string
  type: ToastType
}

const TOAST_COLORS: Record<ToastType, string> = {
  success: 'border-neon-green/50 bg-neon-green/10 text-neon-green',
  error: 'border-red-500/50 bg-red-500/10 text-red-400',
  info: 'border-neon-cyan/50 bg-neon-cyan/10 text-neon-cyan',
}

let toastId = 0

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = ++toastId
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 3000)
  }, [])

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return { toasts, addToast, removeToast }
}

export function ToastContainer({
  toasts,
  removeToast,
}: {
  toasts: Toast[]
  removeToast: (id: number) => void
}) {
  return (
    <div className="fixed top-20 left-0 right-0 z-[60] flex flex-col items-center gap-2 px-4 pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: -20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className={`pointer-events-auto w-full max-w-sm border rounded-xl px-4 py-3 backdrop-blur-md shadow-lg ${TOAST_COLORS[toast.type]}`}
            onClick={() => removeToast(toast.id)}
          >
            <p className="text-sm font-medium text-center">{toast.message}</p>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
