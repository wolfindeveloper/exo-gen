import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Rocket, Zap, FlaskConical } from 'lucide-react'
import { memo } from 'react'
import { playSound } from '../../lib/sounds'
import { useI18n } from '../../hooks/useI18n'

const BottomNav = memo(() => {
  const { t } = useI18n()
  const tabs = [
    { id: 'hangar', label: t('nav.hangar'), icon: Rocket, path: '/hangar' },
    { id: 'galaxy', label: t('nav.galaxy'), icon: Zap, path: '/universe' },
    { id: 'laba', label: t('nav.laboratory'), icon: FlaskConical, path: '/laboratory' },
  ] as const

  return (
  <nav
    className="fixed bottom-0 left-0 right-0 z-50 bg-cosmic-bg/90 backdrop-blur-md border-t border-cosmic-border"
    style={{ paddingBottom: 'max(8px, env(safe-area-inset-bottom))' }}
  >
    <div className="flex items-center justify-around max-w-lg mx-auto">
      {tabs.map((tab) => (
        <NavLink
          key={tab.id}
          to={tab.path}
          end
          className={({ isActive }) =>
            `relative flex flex-col items-center justify-center gap-1 min-w-[90px] min-h-[44px] transition-all duration-200 ${
              isActive ? 'text-neon-cyan' : 'text-gray-500 hover:text-gray-300'
            }`
          }
          onClick={() => playSound('click')}
        >
          {({ isActive }) => (
            <>
              {isActive && (
                <motion.div
                  layoutId="nav-glow"
                  className="absolute inset-0 bg-neon-cyan/10 rounded-xl"
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
              <motion.div
                animate={isActive ? { scale: [1, 1.1, 1] } : { scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <tab.icon className={`w-6 h-6 ${isActive ? 'text-neon-cyan drop-shadow-[0_0_8px_rgba(6,182,212,0.6)]' : ''}`} />
              </motion.div>
              <span className={`text-xs font-semibold relative z-10 ${isActive ? 'text-neon-cyan' : ''}`}>
                {tab.label}
              </span>
              {isActive && (
                <motion.div
                  layoutId="nav-border"
                  className="absolute top-0 left-1/2 -translate-x-1/2 w-12 h-0.5 bg-neon-cyan rounded-full shadow-[0_0_10px_rgba(6,182,212,0.8)]"
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
            </>
          )}
        </NavLink>
      ))}
    </div>
  </nav>
  )
})

BottomNav.displayName = 'BottomNav'
export default BottomNav
