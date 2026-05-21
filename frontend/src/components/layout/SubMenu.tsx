import { memo } from 'react'
import { motion } from 'framer-motion'

interface SubMenuTab {
  id: string
  label: string
}

interface SubMenuProps {
  tabs: SubMenuTab[]
  activeTab: string
  onChange: (id: string) => void
}

const SubMenu = memo(({ tabs, activeTab, onChange }: SubMenuProps) => (
  <div className="flex items-center gap-2 px-0 py-2 max-w-lg mx-auto">
    <div className="flex gap-0.5 bg-cosmic-bg/60 backdrop-blur-sm border border-cosmic-border rounded-xl p-1 w-full">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className="relative flex-1 py-2 px-3 rounded-lg text-xs font-semibold transition-colors"
        >
          {activeTab === tab.id && (
            <motion.div
              layoutId="submenu-active"
              className="absolute inset-0 bg-neon-cyan/15 border border-neon-cyan/40 rounded-lg shadow-[0_0_8px_rgba(6,182,212,0.3)]"
              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            />
          )}
          <span className={`relative z-10 ${activeTab === tab.id ? 'text-neon-cyan' : 'text-gray-400 hover:text-gray-200'}`}>
            {tab.label}
          </span>
        </button>
      ))}
    </div>
  </div>
))

SubMenu.displayName = 'SubMenu'
export default SubMenu
