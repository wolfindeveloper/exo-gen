import { Users, Activity, DollarSign, Map } from 'lucide-react'

const cards = [
  {
    title: 'Пользователи всего',
    icon: Users,
    color: 'text-blue-400',
    bg: 'bg-blue-900/10',
    border: 'border-blue-800/30',
  },
  {
    title: 'DAU (сегодня)',
    icon: Activity,
    color: 'text-green-400',
    bg: 'bg-green-900/10',
    border: 'border-green-800/30',
  },
  {
    title: 'Выручка (Stars)',
    icon: DollarSign,
    color: 'text-amber-400',
    bg: 'bg-amber-900/10',
    border: 'border-amber-800/30',
  },
  {
    title: 'Топ зон',
    icon: Map,
    color: 'text-purple-400',
    bg: 'bg-purple-900/10',
    border: 'border-purple-800/30',
  },
]

export function Dashboard() {
  return (
    <div>
      <h2 className="text-xl font-bold mb-6">Дашборд</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {cards.map((card) => {
          const Icon = card.icon
          return (
            <div
              key={card.title}
              className={`${card.bg} ${card.border} border rounded-xl p-6 flex items-start gap-4`}
            >
              <div className={`${card.color} ${card.bg} p-3 rounded-lg shrink-0`}>
                <Icon size={24} />
              </div>
              <div className="min-w-0">
                <p className="text-sm text-gray-400 mb-1">{card.title}</p>
                <p className="text-lg font-bold text-white">Ожидает API</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
