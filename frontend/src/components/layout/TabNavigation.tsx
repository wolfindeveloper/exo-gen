import { NavLink } from 'react-router-dom'
import { memo } from 'react'

const tabs = [
  { id: 'hangar', label: 'Hangar', icon: '🚀', path: '/hangar' },
  { id: 'universe', label: 'Universe', icon: '🌌', path: '/universe' },
  { id: 'laboratory', label: 'Laboratory', icon: '🧪', path: '/laboratory' },
] as const

const TabNavigation = memo(() => (
  <nav className="fixed bottom-0 left-0 right-0 z-40 bg-cosmic-bg/90 backdrop-blur-md border-t border-cosmic-border">
    <div className="flex items-center justify-around max-w-lg mx-auto">
      {tabs.map((tab) => (
        <NavLink
          key={tab.id}
          to={tab.path}
          end
          className={({ isActive }) =>
            `flex flex-col items-center gap-1 px-4 py-2 min-w-[80px] transition-all duration-200 ${
              isActive
                ? 'text-neon-cyan'
                : 'text-gray-500 hover:text-gray-300'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <span className={`text-xl ${isActive ? 'animate-pulse-slow' : ''}`}>
                {tab.icon}
              </span>
              <span className="text-xs font-medium">{tab.label}</span>
              {isActive && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-neon-cyan rounded-full shadow-glow-cyan" />
              )}
            </>
          )}
        </NavLink>
      ))}
    </div>
  </nav>
))

TabNavigation.displayName = 'TabNavigation'
export default TabNavigation
