import { useEffect } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { ArrowLeft, Boxes, Map, ShoppingBag, BookOpen } from 'lucide-react'

import { useGameStore } from '../../store/game'

const ADMIN_IDS = import.meta.env.VITE_ADMIN_IDS?.split(',').map(Number) || []

export function AdminLayout() {
  const navigate = useNavigate()
  const user = useGameStore((s) => s.user)
  const isAuthReady = useGameStore((s) => s.isAuthReady)

  const tgId = user?.telegram_id ?? window.Telegram?.WebApp?.initDataUnsafe?.user?.id
  const isAdmin = tgId != null && ADMIN_IDS.includes(tgId)

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
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-3 flex items-center justify-between sticky top-0 z-10">
        <h1 className="text-lg font-bold tracking-wide">Админ-панель</h1>
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-sm text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
        >
          <ArrowLeft size={16} />
          Вернуться в игру
        </button>
      </header>

      <div className="flex flex-1">
        <aside className="w-56 bg-gray-800/50 border-r border-gray-700 p-4 space-y-1 shrink-0">
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

        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
