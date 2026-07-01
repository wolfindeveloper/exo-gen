import { useEffect } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { ArrowLeft, Boxes, Map, ShoppingBag, BookOpen } from 'lucide-react'

import { useGameStore } from '../../store/game'

export function AdminLayout() {
  const navigate = useNavigate()
  const isAdmin = useGameStore((s) => s.isAdmin)
  const isAuthReady = useGameStore((s) => s.isAuthReady)

  useEffect(() => {
    if (isAuthReady && !isAdmin) {
      navigate('/', { replace: true })
    }
  }, [isAuthReady, isAdmin, navigate])

  if (!isAuthReady) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <p className="text-gray-500 animate-pulse">Загрузка...</p>
      </div>
    )
  }

  if (!isAdmin) return null

  const navItems = [
    { to: '/admin/items', label: 'Предметы', icon: Boxes },
    { to: '/admin/zones', label: 'Зоны', icon: Map },
    { to: '/admin/shop', label: 'Магазин', icon: ShoppingBag },
    { to: '/admin/guide', label: 'Гайд', icon: BookOpen },
  ]

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between sticky top-0 z-20">
        <h1 className="text-base font-bold tracking-wide">Админ-панель</h1>
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 text-sm text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 px-3 py-1.5 rounded-lg transition-colors"
        >
          <ArrowLeft size={16} />
          <span className="hidden sm:inline">Вернуться в игру</span>
          <span className="sm:hidden">Выйти</span>
        </button>
      </header>

      {/* Mobile: horizontal tabs */}
      <nav className="md:hidden flex gap-1 overflow-x-auto bg-gray-800/50 border-b border-gray-700 px-2 py-2 sticky top-[57px] z-10">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`
              }
            >
              <Icon size={15} />
              {item.label}
            </NavLink>
          )
        })}
      </nav>

      <div className="flex flex-1 overflow-hidden">
        {/* Desktop: sidebar */}
        <aside className="hidden md:block w-52 bg-gray-800/50 border-r border-gray-700 p-3 space-y-1 shrink-0 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                  }`
                }
              >
                <Icon size={18} />
                {item.label}
              </NavLink>
            )
          })}
        </aside>

        <main className="flex-1 p-4 md:p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
