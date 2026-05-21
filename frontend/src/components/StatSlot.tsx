import { motion } from 'framer-motion'
import type { LucideIcon } from 'lucide-react'

interface StatSlotProps {
  icon: LucideIcon
  label: string
  value: string | number
  valueColor?: string
  delay?: number
}

export function StatSlot({ icon: Icon, label, value, valueColor = 'text-neon-cyan', delay = 0 }: StatSlotProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="relative group"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/10 to-neon-purple/10 rounded-xl blur-xl group-hover:opacity-80 transition-opacity opacity-50" />
      <div className="relative bg-cosmic-bg/60 backdrop-blur-md border border-neon-cyan/20 rounded-xl p-3 hover:border-neon-cyan/40 transition-colors">
        <div className="flex flex-col items-center gap-1.5">
          <Icon className="w-5 h-5 text-neon-cyan/70" />
          <span className="text-[10px] uppercase tracking-widest text-gray-500 font-medium">{label}</span>
          <span className={`text-lg font-bold ${valueColor} tracking-wide`}>{value}</span>
        </div>
      </div>
    </motion.div>
  )
}
