import { useCallback } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { BookOpen, Globe2, Package, Rocket, Settings, ShoppingBag, Trophy, User } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

import { useNotifications } from '../hooks/useNotifications'
import { useTranslate } from '../hooks/useTranslate'
import { useSettingsStore } from '../store/settings'

const nav = [
  { path: '/', icon: Rocket, key: 'nav.hangar' },
  { path: '/guide', icon: BookOpen, key: 'nav.guide' },
  { path: '/galaxy', icon: Globe2, key: 'nav.map' },
  { path: '/inventory', icon: Package, key: 'nav.inv' },
  { path: '/profile', icon: User, key: 'nav.profile' },
  { path: '/shop', icon: ShoppingBag, key: 'nav.shop' },
  { path: '/leaderboard', icon: Trophy, key: 'nav.leaders' },
]

function BadgeDot({ color }: { color: string }) {
  return (
    <motion.span
      className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full"
      style={{
        backgroundColor: color,
        boxShadow: `0 0 6px ${color}`,
      }}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      exit={{ scale: 0 }}
      transition={{ type: 'spring', stiffness: 500, damping: 20 }}
    >
      <span
        className="absolute inset-0 rounded-full animate-ping"
        style={{ backgroundColor: color, opacity: 0.5 }}
      />
    </motion.span>
  )
}

function NavIcon({ icon: Icon, active }: { icon: typeof Rocket; active: boolean }) {
  return (
    <Icon
      size={20}
      strokeWidth={1.5}
      className={`transition-all duration-200 ${
        active
          ? 'text-white drop-shadow-[0_0_8px_rgba(34,211,238,0.6)]'
          : 'text-slate-500'
      }`}
    />
  )
}

export function NavBar() {
  const location = useLocation()
  const isCockpit = location.pathname === '/'
  const reduceMotion = useReducedMotion()
  const setSettingsOpen = useSettingsStore((s) => s.setSettingsOpen)
  const t = useTranslate()
  const { hasCompletedExpedition, hasUnlockedGuideEntry, hasUnclaimedReward } = useNotifications()

  const handleSettings = useCallback(() => setSettingsOpen(true), [setSettingsOpen])

  const spring = reduceMotion
    ? { duration: 0 }
    : { type: 'spring' as const, stiffness: 400, damping: 32 }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 px-3 pb-3 safe-area-pb pointer-events-none">
      <div
        className={`max-w-lg mx-auto rounded-[28px] border backdrop-blur-[20px] shadow-[0_-8px_40px_rgba(0,0,0,0.45)] pointer-events-auto overflow-hidden ${
          isCockpit
            ? 'bg-space-900/55 border-cyan-500/[0.08]'
            : 'bg-space-900/75 border-white/10'
        }`}
      >
        <div className="flex items-stretch px-1.5">
          {nav.map((item) => {
            const active = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className="flex-1 flex flex-col items-center justify-center h-[60px] relative"
              >
                {active && (
                  <motion.span
                    layoutId="nav-pill"
                    className="absolute inset-y-1.5 inset-x-0.5 rounded-2xl bg-gradient-to-b from-neon-cyan/[0.14] to-neon-purple/[0.14] border border-white/10"
                    transition={spring}
                  />
                )}
                {active && (
                  <motion.span
                    layoutId="nav-line"
                    className="absolute bottom-0 left-5 right-5 h-[2px] rounded-full bg-gradient-to-r from-neon-cyan/50 via-neon-cyan to-neon-purple/50 shadow-[0_0_8px_rgba(34,211,238,0.5)]"
                    transition={spring}
                  />
                )}
                <motion.span
                  whileTap={reduceMotion ? undefined : { scale: 0.85 }}
                  className="relative flex flex-col items-center justify-center"
                >
                  <motion.span
                    animate={{ y: active ? -5 : 0 }}
                    transition={spring}
                    className="relative flex items-center justify-center"
                  >
                    <NavIcon icon={item.icon} active={active} />
                    <AnimatePresence>
                      {item.path === '/' && hasCompletedExpedition && (
                        <BadgeDot color="#22c55e" />
                      )}
                      {item.path === '/guide' && hasUnlockedGuideEntry && (
                        <BadgeDot color="#a855f7" />
                      )}
                      {item.path === '/guide' && !hasUnlockedGuideEntry && hasUnclaimedReward && (
                        <BadgeDot color="#f59e0b" />
                      )}
                    </AnimatePresence>
                  </motion.span>
                  <AnimatePresence>
                    {active && (
                      <motion.span
                        key="label"
                        initial={{ opacity: 0, y: 4 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 4 }}
                        transition={reduceMotion ? { duration: 0 } : { type: 'spring', stiffness: 500, damping: 30 }}
                        className="absolute top-[23px] font-display text-[9px] uppercase tracking-wider whitespace-nowrap text-neon-cyan"
                      >
                        {t(item.key)}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </motion.span>
              </Link>
            )
          })}

          <div className="flex items-center border-l border-white/[0.06] pl-1.5 ml-1">
            <button
              onClick={handleSettings}
              className="flex items-center justify-center w-[46px] h-[46px] rounded-2xl border border-white/[0.08] bg-white/[0.03] transition-colors text-slate-500 hover:text-slate-300 hover:bg-white/[0.06]"
              aria-label="Settings"
            >
              <motion.span
                whileTap={reduceMotion ? undefined : { rotate: 90, scale: 0.9 }}
                transition={reduceMotion ? { duration: 0 } : { type: 'spring', stiffness: 400, damping: 20 }}
                className="flex"
              >
                <Settings size={18} strokeWidth={1.5} />
              </motion.span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
