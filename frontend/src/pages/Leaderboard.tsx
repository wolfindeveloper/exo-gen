import { useCallback, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { motion } from 'motion/react'
import { useNavigate } from 'react-router-dom'
import { Trophy, Medal, Crown, ChevronDown, ArrowUp, ArrowDown } from 'lucide-react'
import { useGameStore } from '../store/game'
import { Skeleton } from '../components/Skeleton'
import { PullToRefresh } from '../components/PullToRefresh'
import { PageTransition } from '../components/PageTransition'
import { XGenIcon } from '../components/XGenIcon'
import { fadeIn, staggerContainer } from '../lib/animations'
import { getAvatarUrl, hapticImpact } from '../lib/telegram'

type Tab = 'xp' | 'expeditions' | 'artifacts' | 'xgen' | 'articles'

const TABS: { key: Tab; label: string; icon: ReactNode }[] = [
  { key: 'xp', label: 'Уровень', icon: '⭐' },
  { key: 'expeditions', label: 'Экспедиции', icon: '🚀' },
  { key: 'artifacts', label: 'Артефакты', icon: '✨' },
  { key: 'xgen', label: 'XGen', icon: <XGenIcon className="h-3 w-3" /> },
  { key: 'articles', label: 'Статьи', icon: '📖' },
]

const PREV_RANK_KEY = 'leaderboard/prev_ranks'

function loadPrevRanks(): Record<string, number> {
  try {
    return JSON.parse(localStorage.getItem(PREV_RANK_KEY) ?? '{}')
  } catch {
    return {}
  }
}

function savePrevRank(tab: string, rank: number) {
  const prev = loadPrevRanks()
  prev[tab] = rank
  localStorage.setItem(PREV_RANK_KEY, JSON.stringify(prev))
}

function getRankIcon(rank: number) {
  if (rank === 1) return <Crown size={16} className="text-amber-400" />
  if (rank === 2) return <Medal size={16} className="text-slate-300" />
  if (rank === 3) return <Medal size={16} className="text-amber-700" />
  return <span className="text-[11px] text-slate-500 font-mono w-4 text-center">{rank}</span>
}

function RankArrow({ current, previous }: { current: number; previous: number }) {
  if (!previous || previous === current) return null
  if (current < previous) {
    return <ArrowUp size={12} className="text-green-400 shrink-0" />
  }
  return <ArrowDown size={12} className="text-red-400 shrink-0" />
}

export function Leaderboard() {
  const [tab, setTab] = useState<Tab>('xp')
  const user = useGameStore((s) => s.user)
  const leaderboard = useGameStore((s) => s.leaderboard)
  const loadLeaderboard = useGameStore((s) => s.loadLeaderboard)
  const myRowRef = useRef<HTMLDivElement>(null)
  const [showStickyBar, setShowStickyBar] = useState(false)
  const stickyObserverRef = useRef<IntersectionObserver | null>(null)
  const navigate = useNavigate()

  const handleRefresh = useCallback(async () => {
    await loadLeaderboard()
  }, [loadLeaderboard])

  useEffect(() => { loadLeaderboard() }, [loadLeaderboard])

  // Auto-scroll to my row after data loads
  useEffect(() => {
    if (!leaderboard) return
    const timer = setTimeout(() => {
      myRowRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 500)
    return () => clearTimeout(timer)
  }, [leaderboard, tab])

  // Store previous rank when leaderboard loads
  useEffect(() => {
    if (!leaderboard) return
    const myRank = tab === 'xp' ? leaderboard.my_rank : leaderboard[tab]?.my_rank
    if (myRank > 0) {
      savePrevRank(tab, myRank)
    }
  }, [leaderboard, tab])

  // IntersectionObserver for sticky bar
  useEffect(() => {
    if (!myRowRef.current) return

    stickyObserverRef.current?.disconnect()
    stickyObserverRef.current = new IntersectionObserver(
      ([entry]) => {
        const visible = entry.isIntersecting
        setShowStickyBar(!visible)
      },
      { threshold: 0, rootMargin: '-80px 0px -80px 0px' }
    )

    if (myRowRef.current) {
      stickyObserverRef.current.observe(myRowRef.current)
    }

    return () => {
      stickyObserverRef.current?.disconnect()
    }
  }, [leaderboard, tab])

  const scrollToMyRow = () => {
    myRowRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  if (!leaderboard) {
    return (
      <PageTransition>
        <div className="px-5 pb-24 pt-4 max-w-md mx-auto">
          <div className="flex items-center gap-2 mb-5">
            <Trophy size={18} className="text-amber-400" />
            <h1 className="font-display text-lg uppercase tracking-widest text-neon-cyan">
              Жители Галактики
            </h1>
          </div>
          <div className="flex gap-1.5 mb-4">
            {TABS.map((t) => (
              <Skeleton key={t.key} variant="text" className="w-20 h-8 rounded-xl" />
            ))}
          </div>
          <Skeleton variant="row" count={8} />
        </div>
      </PageTransition>
    )
  }

  const myTelegramId = user?.telegram_id
  const myAvatarUrl = getAvatarUrl()
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

  const myRank = tab === 'xp' ? leaderboard.my_rank : leaderboard[tab]?.my_rank
  const prevRanks = loadPrevRanks()
  const prevMyRank = prevRanks[tab] ?? 0

  return (
    <PageTransition>
      <PullToRefresh onRefresh={handleRefresh}>
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
                <RankArrow current={myRank} previous={prevMyRank} />
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
          {entries.length === 0 ? (
            <div className="glass-card p-8 text-center">
              <div className="text-3xl mb-3 opacity-40">🏆</div>
              <p className="text-slate-500 text-xs font-display uppercase tracking-wider mb-1">Таблица лидеров пуста</p>
              <p className="text-[11px] text-slate-600 mb-4">Стань первым — отправься в экспедицию!</p>
              <motion.button
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => {
                  hapticImpact('light')
                  navigate('/galaxy')
                }}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-neon-purple/10 border border-neon-purple/25 text-neon-purple text-[10px] font-display uppercase tracking-wider hover:bg-neon-purple/15 transition-colors"
              >
                🌌 К галактике
              </motion.button>
            </div>
          ) : (
            entries.map((e) => {
            const isMe = e.telegramId === myTelegramId
            const showAvatar = isMe && myAvatarUrl
            return (
              <motion.div
                ref={isMe ? myRowRef : undefined}
                key={`${e.rank}-${e.telegramId}`}
                variants={fadeIn}
                className={`glass-card p-3 flex items-center gap-3 ${
                  isMe ? 'border-amber-400/30 bg-amber-500/5 animate-row-pulse' : ''
                }`}
              >
                <div className="w-8 flex justify-center">{getRankIcon(e.rank)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    {showAvatar ? (
                      <img
                        src={myAvatarUrl}
                        alt=""
                        className="w-5 h-5 rounded-full object-cover border border-amber-400/30 shrink-0"
                      />
                    ) : null}
                    <p className={`text-sm font-display truncate ${isMe ? 'text-amber-200' : 'text-slate-200'}`}>
                      {e.name}
                      {isMe && <span className="text-[10px] text-amber-400 ml-1.5 uppercase">(вы)</span>}
                    </p>
                  </div>
                  {e.subValue && (
                    <p className="text-[10px] text-slate-500">{e.subValue}</p>
                  )}
                </div>
                <div className="flex items-center gap-1.5">
                  {isMe && <RankArrow current={e.rank} previous={prevMyRank} />}
                  <span className="text-lg font-display font-mono text-neon-cyan tabular-nums">
                    {e.value}
                  </span>
                </div>
              </motion.div>
            )
          })
        )}
        </motion.div>
      </div>

      {/* Sticky bottom bar */}
      {showStickyBar && myRank > 0 && (
        <div className="fixed bottom-0 left-0 right-0 z-50 px-4 pb-4 pointer-events-none">
          <div className="max-w-md mx-auto pointer-events-auto">
            <div
              onClick={scrollToMyRow}
              className="animate-slide-up glass-card px-4 py-3 border border-amber-400/30 bg-space-800/95 backdrop-blur-md shadow-lg cursor-pointer flex items-center justify-between"
            >
              <div className="flex items-center gap-2">
                {getRankIcon(myRank)}
                <span className="text-sm font-display text-amber-200">
                  Ты на <span className="font-mono text-amber-300">#{myRank}</span> месте
                </span>
                <RankArrow current={myRank} previous={prevMyRank} />
              </div>
              <div className="flex items-center gap-1 text-[10px] text-slate-400">
                <span>К позиции</span>
                <ChevronDown size={14} className="rotate-180" />
              </div>
            </div>
          </div>
        </div>
      )}
      </PullToRefresh>
    </PageTransition>
  )
}
