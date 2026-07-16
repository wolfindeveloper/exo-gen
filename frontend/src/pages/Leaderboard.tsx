import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { Trophy, Medal, Crown } from 'lucide-react'
import { useGameStore } from '../store/game'
import { HudBar } from '../components/HudBar'
import { PageTransition } from '../components/PageTransition'
import { fadeIn, staggerContainer } from '../lib/animations'

type Tab = 'xp' | 'expeditions' | 'artifacts' | 'xgen' | 'articles'

const TABS: { key: Tab; label: string; icon: string }[] = [
  { key: 'xp', label: 'Уровень', icon: '⭐' },
  { key: 'expeditions', label: 'Экспедиции', icon: '🚀' },
  { key: 'artifacts', label: 'Артефакты', icon: '✨' },
  { key: 'xgen', label: 'XGen', icon: '💎' },
  { key: 'articles', label: 'Статьи', icon: '📖' },
]

function getRankIcon(rank: number) {
  if (rank === 1) return <Crown size={16} className="text-amber-400" />
  if (rank === 2) return <Medal size={16} className="text-slate-300" />
  if (rank === 3) return <Medal size={16} className="text-amber-700" />
  return <span className="text-[11px] text-slate-500 font-mono w-4 text-center">{rank}</span>
}

export function Leaderboard() {
  const [tab, setTab] = useState<Tab>('xp')
  const user = useGameStore((s) => s.user)
  const leaderboard = useGameStore((s) => s.leaderboard)
  const loadLeaderboard = useGameStore((s) => s.loadLeaderboard)

  useEffect(() => { loadLeaderboard() }, [loadLeaderboard])

  if (!leaderboard) {
    return <div className="p-6 text-center text-slate-500">Загрузка...</div>
  }

  const myTelegramId = user?.telegram_id
  const entries =
    tab === 'xp'
      ? leaderboard.top_players.map((p) => ({
          rank: p.rank, telegramId: p.telegram_id,
          name: p.username ?? `Игрок ${p.telegram_id}`,
          value: p.level, subValue: `${p.xp} XP`,
        }))
      : leaderboard[tab].top.map((e) => ({
          rank: e.rank, telegramId: e.telegram_id,
          name: e.username ?? `Игрок ${e.telegram_id}`,
          value: e.value,
          subValue: undefined as string | undefined,
        }))

  const myRank = tab === 'xp' ? leaderboard.my_rank : leaderboard[tab].my_rank

  return (
    <PageTransition>
      <HudBar />
      <div className="px-5 pb-24 pt-4 max-w-md mx-auto">
        <div className="flex items-center gap-2 mb-5">
          <Trophy size={18} className="text-amber-400" />
          <h1 className="font-display text-lg uppercase tracking-widest text-neon-cyan">
            Жители Галактики
          </h1>
        </div>

        {/* Tabs */}
        <div className="flex gap-1.5 mb-4 overflow-x-auto pb-1">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-3 py-2 rounded-xl text-[10px] font-display uppercase tracking-wider border whitespace-nowrap transition ${
                tab === t.key
                  ? 'text-neon-cyan border-neon-cyan/30 bg-neon-cyan/10'
                  : 'text-slate-500 border-white/10 hover:border-white/20'
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {/* My rank card */}
        {myRank > 0 && (
          <div className="glass-card p-3 mb-4 border-amber-400/20 bg-amber-500/5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getRankIcon(myRank)}
                <span className="text-[10px] font-display uppercase tracking-wider text-slate-400">
                  Моё место
                </span>
              </div>
              <span className="text-lg font-display text-amber-300 font-mono">#{myRank}</span>
            </div>
          </div>
        )}

        {/* Top list */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="space-y-2"
        >
          {entries.map((e) => {
            const isMe = e.telegramId === myTelegramId
            return (
              <motion.div
                key={`${e.rank}-${e.telegramId}`}
                variants={fadeIn}
                className={`glass-card p-3 flex items-center gap-3 ${
                  isMe ? 'border-amber-400/30 bg-amber-500/5' : ''
                }`}
              >
                <div className="w-8 flex justify-center">{getRankIcon(e.rank)}</div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-display truncate ${isMe ? 'text-amber-200' : 'text-slate-200'}`}>
                    {e.name}
                    {isMe && <span className="text-[8px] text-amber-400 ml-1.5 uppercase">(вы)</span>}
                  </p>
                  {e.subValue && (
                    <p className="text-[10px] text-slate-500">{e.subValue}</p>
                  )}
                </div>
                <span className="text-lg font-display font-mono text-neon-cyan tabular-nums">
                  {e.value}
                </span>
              </motion.div>
            )
          })}
        </motion.div>
      </div>
    </PageTransition>
  )
}
