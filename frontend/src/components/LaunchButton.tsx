import { motion } from 'framer-motion'
import { Rocket } from 'lucide-react'
import { playSound } from '../lib/sounds'

interface LaunchButtonProps {
  onClick: () => void
  disabled?: boolean
  label?: string
}

export function LaunchButton({ onClick, disabled = false, label = 'В экспедицию' }: LaunchButtonProps) {
  const handleClick = () => {
    playSound('expedition')
    onClick()
  }

  return (
    <motion.button
      onClick={handleClick}
      disabled={disabled}
      className="relative w-full group disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px]"
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
        className="relative px-6 py-4 rounded-2xl border border-cyan-400/50 backdrop-blur-sm overflow-hidden"
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
            animate={{ rotate: [0, -10, 10, 0] }}
            transition={{ duration: 1, repeat: Infinity, ease: 'easeInOut' }}
          >
            <Rocket className="w-6 h-6 text-cyan-300" />
          </motion.div>
          <span className="text-lg font-bold tracking-widest text-white uppercase">{label}</span>
        </div>
      </div>
    </motion.button>
  )
}
