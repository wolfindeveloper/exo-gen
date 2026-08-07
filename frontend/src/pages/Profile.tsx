import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { useNavigate } from 'react-router-dom'
import {
  Award, BookOpen, Briefcase, Clock, Flame, Fuel,
  Hammer, Lock, Package, Pencil, Rocket, Shield, Sparkles,
  Star, Trophy, Unlock, Zap,
} from 'lucide-react'

import { fadeIn, staggerContainer } from '../lib/animations'
import { Skeleton } from '../components/Skeleton'
import { PullToRefresh } from '../components/PullToRefresh'
import { useCountUp } from '../hooks/useCountUp'
import { calculateLevel, getNextLevelXp, getXpProgress, getXpToNextLevel } from '../lib/xp'
import {
  getMaxArtifactSlots,
  getNextSlotUnlock,
  getNextZoneUnlock,
  ZONE_UNLOCK_TABLE,
} from '../lib/progression'
import { getTierForLevel, findRank } from '../lib/ranks'
import { getAvatarUrl, getFirstName } from '../lib/telegram'
import { useGameStore } from '../store/game'
import { FragmentIcon } from '../components/FragmentIcon'
import type { UserStats } from '../types'

const tierGradients = [
  'from-cyan-500/20 to-blue-600/20',
  'from-green-500/20 to-emerald-600/20',
  'from-purple-500/20 to-violet-600/20',
  'from-amber-500/20 to-orange-600/20',
  'from-red-500/20 to-rose-600/20',
]
const tierRingColors = ['#22d3ee', '#22c55e', '#a855f7', '#f59e0b', '#ef4444']

const ACHIEVEMENT_DEFS: Record<string, {
  icon: typeof Award; label: string; desc: string; reward: string
  check: (s: UserStats, streak: number) => boolean
  progress?: (s: UserStats, streak: number) => { current: number; max: number }
}> = {
  engineer: {
    icon: Hammer, label: 'Инженер', desc: 'Создайте первый артефакт', reward: '+50 XP',
    check: (s) => s.artifacts_crafted > 0,
  },
  explorer: {
    icon: Rocket, label: 'Исследователь', desc: 'Проведите 10 экспедиций', reward: '+100 XP · 10 ✦',
    check: (s) => s.completed_expeditions >= 10,
    progress: (s) => ({ current: s.completed_expeditions, max: 10 }),
  },
  veteran: {
    icon: Trophy, label: 'Ветеран', desc: 'Проведите 30 дней в проекте', reward: '+200 XP · 25 ✦',
    check: (s) => s.joined_days > 30,
    progress: (s) => ({ current: s.joined_days, max: 30 }),
  },
  collector: {
    icon: Sparkles, label: 'Коллекционер', desc: 'Соберите 5 разных артефактов', reward: '+100 XP · 10 ✦',
    check: (s) => s.unique_artifacts >= 5,
    progress: (s) => ({ current: s.unique_artifacts, max: 5 }),
  },
  hardworker: {
    icon: Briefcase, label: 'Трудоголик', desc: 'Завершите 25 экспедиций', reward: '+200 XP · 25 ✦',
    check: (s) => s.completed_expeditions >= 25,
    progress: (s) => ({ current: s.completed_expeditions, max: 25 }),
  },
  mechanic: {
    icon: Zap, label: 'Механик', desc: 'Экипируйте артефакты во все 8 слотов', reward: '+150 XP · 15 ✦',
    check: (s) => s.equipped_artifacts_count >= 8,
    progress: (s) => ({ current: s.equipped_artifacts_count, max: 8 }),
  },
  scholar: {
    icon: BookOpen, label: 'Эрудит', desc: 'Изучите 20 записей в Гайде', reward: '+150 XP · 15 ✦',
    check: (s) => s.guide_progress.entries_researched >= 20,
    progress: (s) => ({ current: s.guide_progress.entries_researched, max: 20 }),
  },
  lucky: {
    icon: Star, label: 'Счастливчик', desc: 'Исправьте 5 глитчей', reward: '+100 XP · 10 ✦',
    check: (s) => s.glitches_fixed >= 5,
    progress: (s) => ({ current: s.glitches_fixed, max: 5 }),
  },
  steadfast: {
    icon: Flame, label: 'Стойкий', desc: 'Достигните 7-дневного стрика', reward: '+100 XP · 10 ✦',
    check: (_, streak) => streak >= 7,
    progress: (_, streak) => ({ current: streak, max: 7 }),
  },
}

export function Profile() {
  const navigate = useNavigate()
  const user = useGameStore((s) => s.user)
  const stats = useGameStore((s) => s.stats)
  const ranksContent = useGameStore((s) => s.ranksContent)
  const ships = useGameStore((s) => s.ships)
  const achievements = useGameStore((s) => s.achievements)
  const loadProfile = useGameStore((s) => s.loadProfile)
  const loadStats = useGameStore((s) => s.loadStats)
  const loadAchievements = useGameStore((s) => s.loadAchievements)
  const claimAchievement = useGameStore((s) => s.claimAchievement)
  const updateNickname = useGameStore((s) => s.updateNickname)
  const artifactsContent = useGameStore((s) => s.artifactsContent)
  const zonesContent = useGameStore((s) => s.zonesContent)
  const resourcesContent = useGameStore((s) => s.resourcesContent)
  const isAdmin = useGameStore((s) => s.isAdmin)
  const [editing, setEditing] = useState(false)
  const [nick, setNick] = useState('')
  const [claiming, setClaiming] = useState<string | null>(null)
  const [claimResult, setClaimResult] = useState<{ aid: string; xp: number; xgen: number } | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const avatarUrl = getAvatarUrl()
  const first = getFirstName()

  const xp = user?.xp ?? 0
  const level = calculateLevel(xp)
  const nextLevelXp = getNextLevelXp(level)
  const xpPercent = getXpProgress(xp, level)
  const xpToNext = getXpToNextLevel(xp, level)
  const tier = getTierForLevel(level)
  const rank = findRank(level, ranksContent)
  const maxSlots = getMaxArtifactSlots(level)
  const nextSlotUnlock = getNextSlotUnlock(level)
  const nextZoneUnlock = getNextZoneUnlock(level)

  const mainShip = ships[0] ?? null
  const shipConfig = useMemo(
    () => useGameStore.getState().shipsContent.find((c) => c.id === mainShip?.id),
    [mainShip],
  )

  const equippedCount = useMemo(
    () => mainShip?.equipment?.artifacts?.length ?? 0,
    [mainShip],
  )

  const claimedSet = useMemo(() => new Set(achievements.filter((a) => a.claimed).map((a) => a.achievement_id)), [achievements])

  const levelXpCount = useCountUp(xp, 1200)
  const nextXpCount = useCountUp(nextLevelXp, 1200)
  const streakCount = useCountUp(user?.daily_streak ?? 0, 1000)
  const starsCount = useCountUp(user?.balance_stars ?? 0, 1000)
  const xgenCount = useCountUp(user?.xgen_balance ?? 0, 1200)
  const fragmentsCount = useCountUp(user?.fragments_balance ?? 0, 1000)
  const artifactsFoundCount = useCountUp(stats?.artifacts_found ?? 0, 1000)
  const xgenEarnedTotalCount = useCountUp(stats?.xgen_earned_total ?? 0, 1200)
  const fragmentsEarnedTotalCount = useCountUp(stats?.fragments_earned_total ?? 0, 1000)
  const joinedDaysCount = useCountUp(stats?.joined_days ?? 0, 1000)

  useEffect(() => {
    loadProfile()
    loadStats()
    loadAchievements()
  }, [loadProfile, loadStats, loadAchievements])

  const handleRefresh = useCallback(async () => {
    await Promise.all([loadProfile(), loadStats()])
  }, [loadProfile, loadStats])

  const saveNick = useCallback(async () => {
    const trimmed = nick.trim()
    if (trimmed && trimmed !== user?.username) {
      await updateNickname(trimmed)
    }
    setEditing(false)
  }, [nick, user, updateNickname])

  const handleStartEdit = useCallback(() => {
    setNick(user?.username || first || 'Капитан')
    setEditing(true)
    setTimeout(() => inputRef.current?.focus(), 0)
  }, [user, first])

  const handleClaim = useCallback(async (aid: string) => {
    setClaiming(aid)
    try {
      await claimAchievement(aid)
      const def = ACHIEVEMENT_DEFS[aid]
      const xpReward = def.reward.includes('XP') ? parseInt(def.reward.match(/\d+/)?.[0] || '0') : 0
      const xgenReward = def.reward.includes('✦') ? parseInt(def.reward.match(/(\d+)\s*✦/)?.[1] || '0') : 0
      setClaimResult({ aid, xp: xpReward, xgen: xgenReward })
      setTimeout(() => setClaimResult(null), 3000)
    } finally {
      setClaiming(null)
    }
  }, [claimAchievement])

  const nextRank = useMemo(() => {
    const next = ranksContent.find((r) => r.level > level)
    return next ? { title: next.title_key, at: next.level, remaining: next.level - level } : null
  }, [level, ranksContent])

  if (!user) {
    return (
      <div className="p-4 pb-28 space-y-4">
        <Skeleton variant="text" className="w-28 h-6" />
        <Skeleton variant="card" />
        <div className="flex gap-3">
          <Skeleton variant="card" className="flex-1" />
          <Skeleton variant="card" className="flex-1" />
        </div>
        <Skeleton variant="card" />
        <div className="grid grid-cols-2 gap-3">
          <Skeleton variant="card" />
          <Skeleton variant="card" />
        </div>
      </div>
    )
  }

  const safeStats = stats || {
    total_expeditions: 0, completed_expeditions: 0, expeditions_in_progress: 0, failed_expeditions: 0,
    artifacts_found: 0, artifacts_crafted: 0, joined_days: 0, total_xp_earned: 0,
    xgen_earned_total: 0, fragments_earned_total: 0, zones_explored: 0,
    equipped_artifacts_count: 0, unique_artifacts: 0,
    articles_read: 0, articles_total: 0,
    resources: { fuel: 0, repair_kits: 0 },
    guide_progress: { total_chapters: 0, completed_chapters: 0, entries_researched: 0 },
    recent_expeditions: [],
    glitches_fixed: 0, total_purchases: 0,
  } satisfies UserStats

  const zoneName = (id: string) => zonesContent.find((z) => z.id === id)?.name || id
  const itemName = (id: string) => {
    const r = resourcesContent.find((r) => r.id === id)
    if (r) return r.name_key
    const a = artifactsContent.find((a) => a.id === id)
    if (a) return a.name_key
    return id
  }
  const readableLoot = (summary: string) =>
    summary.split(', ').map((part) => {
      const m = part.match(/^(.+?)x(\d+)$/)
      return m ? `${itemName(m[1])} x${m[2]}` : part
    }).join(', ')

  const guideTotal = stats?.guide_progress.total_chapters ?? 0
  const guideCompleted = stats?.guide_progress.completed_chapters ?? 0
  const guidePercent = guideTotal > 0 ? (guideCompleted / guideTotal) * 100 : 0

  const claimableCount = Object.entries(ACHIEVEMENT_DEFS).filter(
    ([aid, def]) => def.check(safeStats, user.daily_streak ?? 0) && !claimedSet.has(aid),
  ).length

  return (
    <PullToRefresh onRefresh={handleRefresh}>
    <div className="p-4 pb-28">
      <motion.header className="mb-6" variants={fadeIn} initial="hidden" animate="visible">
        <h1 className="font-display text-lg uppercase tracking-[0.2em] text-neon-cyan">Профиль</h1>
      </motion.header>

      {/* Claim result toast */}
      <AnimatePresence>
        {claimResult && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10 }}
            className="glass-card p-3 mb-4 flex items-center gap-3 border-neon-amber/20 bg-neon-amber/5"
          >
            <Award size={18} className="text-amber-400 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-display text-amber-400 uppercase tracking-wider">Награда получена!</p>
              <p className="text-[10px] text-slate-400 mt-0.5">
                +{claimResult.xp} XP{claimResult.xgen > 0 ? ` · +${claimResult.xgen} ✦` : ''}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hero */}
      <motion.div
        className="glass-card p-5 mb-4 relative overflow-hidden"
        variants={fadeIn}
        initial="hidden"
        animate="visible"
      >
        <div className={`absolute inset-0 bg-gradient-to-b ${tierGradients[tier]} opacity-30`} />
        <div className="relative">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-[72px] h-[72px] rounded-full bg-gradient-to-br from-neon-cyan to-neon-purple overflow-hidden ring-2 ring-white/10 shrink-0">
              {avatarUrl ? (
                <img src={avatarUrl} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-2xl font-display text-white">
                  {(first || '?')[0]}
                </div>
              )}
            </div>
            <div className="flex-1 min-w-0 text-left">
              {editing ? (
                <input
                  ref={inputRef}
                  type="text"
                  value={nick}
                  onChange={(e) => setNick(e.target.value)}
                  onBlur={saveNick}
                  onKeyDown={(e) => { if (e.key === 'Enter') saveNick() }}
                  className="bg-space-600 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-neon-cyan/50 w-full"
                  maxLength={32}
                  autoFocus
                />
              ) : (
                <div className="flex items-center gap-1.5 min-w-0">
                  <span className="text-base text-slate-200 font-medium truncate">{user.username || first || 'Капитан'}</span>
                  <button
                    onClick={handleStartEdit}
                    className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
                    aria-label="Редактировать имя"
                  >
                    <Pencil size={14} />
                  </button>
                </div>
              )}
              {rank && (
                <motion.div
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[9px] font-display uppercase tracking-wider mt-1.5 border"
                  style={{
                    borderColor: `${tierRingColors[tier - 1]}33`,
                    color: tierRingColors[tier - 1],
                    backgroundColor: `${tierRingColors[tier - 1]}10`,
                  }}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 15, delay: 0.3 }}
                >
                  <Award size={10} />
                  {rank.title_key}
                </motion.div>
              )}
              <p className="text-[10px] text-slate-500 mt-1 truncate">{rank?.description_key || ''}</p>
            </div>
          </div>

          {/* XP progress */}
          <div>
            <div className="flex items-center justify-between text-[10px] mb-1.5">
              <span className="text-slate-500 font-display uppercase tracking-wider">Уровень {level}</span>
              <span className="text-slate-500 font-mono tabular-nums">
                <span className="text-neon-cyan">{levelXpCount}</span> / {nextXpCount} XP
              </span>
            </div>
            <div className="relative h-2.5 bg-space-500 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full relative"
                style={{
                  background: `linear-gradient(90deg, ${tierRingColors[tier - 1]}, ${tierRingColors[Math.min(tier, 4)] || '#a855f7'})`,
                  boxShadow: `0 0 8px ${tierRingColors[tier - 1]}44`,
                }}
                initial={{ width: 0 }}
                animate={{ width: `${xpPercent}%` }}
                transition={{ duration: 1.2, ease: 'easeOut' }}
              >
                {xpPercent > 80 && (
                  <motion.div
                    className="absolute inset-y-0 right-0 w-4 rounded-full bg-white/30"
                    animate={{ opacity: [0.3, 0.6, 0.3] }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                  />
                )}
              </motion.div>
            </div>
            <p className="text-[10px] text-slate-600 mt-1.5 text-center">
              До уровня {level + 1}: ещё <span className="text-slate-400 font-mono">{xpToNext}</span> XP
            </p>
          </div>

          {nextRank && (
            <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-center gap-1.5 text-[10px] text-slate-500">
              <Trophy size={10} className="text-amber-500/60" />
              Следующий ранг: <span className="text-amber-400/80 font-display">{nextRank.title}</span>
              <span className="text-slate-600">через {nextRank.remaining} ур.</span>
            </div>
          )}
        </div>
      </motion.div>

      {/* Wallet */}
      <motion.div
        className="grid grid-cols-4 gap-2 mb-4"
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
      >
        <BalanceCard title="XGEN" value={xgenCount} accent="#22d3ee" pulse>
          <div className="text-[15px] font-display text-neon-cyan leading-none">✦</div>
        </BalanceCard>
        <BalanceCard title="STARS" value={starsCount} accent="#f59e0b">
          <Star size={16} className="text-amber-400" />
        </BalanceCard>
        <BalanceCard title="ФРАГМ" value={fragmentsCount} accent="#a855f7">
          <FragmentIcon className="h-4 w-4" />
        </BalanceCard>
        <BalanceCard title="СТРИК" value={streakCount} accent="#ef4444" subtitle={`+${(user.daily_streak + 1) * 10} XP`}>
          <Flame size={16} className="text-red-400" />
        </BalanceCard>
      </motion.div>

      {/* Progression */}
      <motion.div
        className="glass-card p-4 mb-4"
        variants={fadeIn}
        initial="hidden"
        animate="visible"
      >
        <div className="flex items-center gap-2 mb-4">
          <Sparkles size={14} className="text-amber-400" />
          <span className="text-[10px] font-display uppercase tracking-wider text-slate-400">
            Прогресс
          </span>
        </div>

        {/* Zones tier progress */}
        <div className="mb-5">
          <p className="text-[9px] text-slate-500 mb-2 uppercase tracking-wider">Зоны галактики</p>
          <div className="flex gap-1.5">
            {[1, 2, 3, 4, 5].map((tierId) => {
              const required = ZONE_UNLOCK_TABLE[tierId]
              const isUnlocked = level >= required
              const TIER_HEX: Record<number, string> = { 1: '#22d3ee', 2: '#22c55e', 3: '#a855f7', 4: '#fbbf24', 5: '#ef4444' }
              const hex = TIER_HEX[tierId]
              const tierStyle = isUnlocked
                ? { borderColor: `${hex}55`, backgroundColor: `${hex}22` }
                : { borderColor: 'rgba(100,116,139,0.3)', backgroundColor: 'rgba(15,20,32,0.3)' }
              return (
                <div
                  key={tierId}
                  className="flex-1 aspect-square rounded-lg flex flex-col items-center justify-center border"
                  style={tierStyle}
                >
                  <span
                    className="text-[10px] font-display font-bold"
                    style={{ color: isUnlocked ? hex : '#475569' }}
                  >
                    T{tierId}
                  </span>
                  {isUnlocked ? (
                    <Unlock size={8} className="mt-0.5" style={{ color: hex }} />
                  ) : (
                    <div className="flex items-center gap-0.5 mt-0.5">
                      <Lock size={6} className="text-slate-600" />
                      <span className="text-[10px] text-slate-600 font-mono">{required}</span>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
          <div className="flex items-center justify-between gap-2 mt-2.5">
            <p className="text-[10px] text-slate-600">
              {nextZoneUnlock ? (
                <>Зоны T{nextZoneUnlock.tier} откроются на <span className="text-amber-400">LVL {nextZoneUnlock.requiredLevel}</span></>
              ) : (
                <span className="text-neon-green">✓ Все зоны открыты</span>
              )}
            </p>
            {nextZoneUnlock && (
              <button
                onClick={() => navigate('/galaxy')}
                className="shrink-0 text-[10px] px-3 h-7 rounded-lg bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/20 font-display uppercase tracking-wider active:bg-neon-cyan/20 transition-colors"
              >
                К галактике →
              </button>
            )}
          </div>
        </div>

        {/* Artifact slots */}
        <div className="mb-5">
          <div className="flex items-center justify-between mb-2">
            <p className="text-[9px] text-slate-500 uppercase tracking-wider">Слоты артефактов</p>
            <span className="text-[10px] text-slate-500 truncate ml-2">
              {shipConfig?.name_key || 'Vega MK-II'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-space-600 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-neon-cyan to-neon-purple"
                initial={{ width: 0 }}
                animate={{ width: `${(maxSlots / 8) * 100}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </div>
            <span className="text-[10px] font-mono text-slate-300 tabular-nums">
              {maxSlots}/8
            </span>
          </div>
          <p className="text-[10px] text-slate-600 mt-1.5">
            Экипировано: <span className="text-slate-400 font-mono">{equippedCount}</span>
            {nextSlotUnlock ? (
              <> · +{nextSlotUnlock.newSlotCount - maxSlots} слота на{' '}
              <span className="text-amber-400">LVL {nextSlotUnlock.requiredLevel}</span></>
            ) : (
              <> · <span className="text-neon-green">все слоты открыты</span></>
            )}
          </p>
        </div>

        {/* Guide progress */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-[9px] text-slate-500 uppercase tracking-wider">Путеводитель</p>
            <span className="text-[10px] font-mono text-neon-purple tabular-nums">
              {guideCompleted}/{guideTotal} глав
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-space-600 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-neon-purple/80 to-fuchsia-500"
                initial={{ width: 0 }}
                animate={{ width: `${guidePercent}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </div>
            <BookOpen size={14} className="text-neon-purple shrink-0" />
          </div>
          <div className="flex items-center justify-between gap-2 mt-1.5">
            <p className="text-[10px] text-slate-600">{stats?.guide_progress.entries_researched ?? 0} записей изучено</p>
            <button
              onClick={() => navigate('/guide')}
              className="shrink-0 text-[10px] px-3 h-7 rounded-lg bg-neon-purple/10 text-neon-purple border border-neon-purple/20 font-display uppercase tracking-wider active:bg-neon-purple/20 transition-colors"
            >
              В гайд →
            </button>
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <h2 className="text-[10px] font-display uppercase tracking-[0.15em] text-slate-500 mb-3">Статистика</h2>

      {/* Expedition success */}
      {stats && stats.total_expeditions > 0 && (
        <motion.div
          className="glass-card p-4 mb-3 flex items-center gap-4"
          variants={fadeIn}
          initial="hidden"
          animate="visible"
        >
          <div className="relative shrink-0">
            <svg width="56" height="56">
              <circle cx="28" cy="28" r="24" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="5" />
              <motion.circle
                cx="28" cy="28" r="24" fill="none"
                stroke="#22c55e" strokeWidth="5" strokeLinecap="round"
                strokeDasharray={2 * Math.PI * 24}
                initial={{ strokeDashoffset: 2 * Math.PI * 24 }}
                animate={{ strokeDashoffset: 2 * Math.PI * 24 * (1 - stats.completed_expeditions / stats.total_expeditions) }}
                transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
                transform="rotate(-90 28 28)"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-display text-neon-green">
                {Math.round(stats.completed_expeditions / stats.total_expeditions * 100)}%
              </span>
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-slate-300 font-medium">Успешность экспедиций</p>
            <div className="flex gap-3 text-[10px] text-slate-500 mt-1">
              <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-neon-green" /> {stats.completed_expeditions} успешно</span>
              <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-red-500" /> {stats.failed_expeditions} провалено</span>
            </div>
            {stats.expeditions_in_progress > 0 && (
              <p className="text-[10px] text-slate-600 mt-1">Активных: {stats.expeditions_in_progress}</p>
            )}
          </div>
        </motion.div>
      )}

      {/* Stat cards grid */}
      <motion.div
        className="grid grid-cols-2 gap-3 mb-4"
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={fadeIn} className="glass-card p-3">
          <p className="text-[9px] text-slate-500 uppercase tracking-wider mb-1">Артефактов найдено</p>
          <p className="font-display text-xl text-neon-purple tabular-nums">
            {artifactsFoundCount}
          </p>
        </motion.div>

        <motion.div variants={fadeIn} className="glass-card p-3">
          <p className="text-[9px] text-slate-500 uppercase tracking-wider mb-1">XGen заработано</p>
          <p className="font-display text-xl text-amber-400 tabular-nums">
            {xgenEarnedTotalCount}
          </p>
        </motion.div>

        <motion.div variants={fadeIn} className="glass-card p-3">
          <p className="text-[9px] text-slate-500 uppercase tracking-wider mb-1">Фрагментов заработано</p>
          <p className="font-display text-xl text-neon-cyan tabular-nums">
            {fragmentsEarnedTotalCount}
          </p>
        </motion.div>

        <motion.div variants={fadeIn} className="glass-card p-3">
          <p className="text-[9px] text-slate-500 uppercase tracking-wider mb-1">Дней в проекте</p>
          <p className="font-display text-xl text-neon-green tabular-nums">
            {joinedDaysCount}
          </p>
        </motion.div>
      </motion.div>

      {/* Inventory summary */}
      <motion.button
        onClick={() => navigate('/inventory')}
        className="glass-card p-3 mb-4 w-full flex items-center gap-3 text-left active:scale-[0.98] transition-transform"
        variants={fadeIn}
        initial="hidden"
        animate="visible"
      >
        <Package size={16} className="text-neon-cyan shrink-0" />
        <div className="flex-1 min-w-0 flex items-center gap-4 text-[10px] text-slate-400">
          <span><Fuel size={12} className="inline mr-1 text-neon-cyan" />{stats?.resources.fuel ?? 0}</span>
          <span><Shield size={12} className="inline mr-1 text-neon-green" />{stats?.resources.repair_kits ?? 0}</span>
          <span><Sparkles size={12} className="inline mr-1 text-neon-purple" />{stats?.artifacts_crafted ?? 0}</span>
        </div>
        <span className="text-[10px] text-slate-600">Инвентарь →</span>
      </motion.button>

      {/* Artifact showcase */}
      {mainShip && mainShip.equipment?.artifacts && mainShip.equipment.artifacts.length > 0 && (
        <motion.div className="mb-4" variants={fadeIn} initial="hidden" animate="visible">
          <h2 className="text-[10px] font-display uppercase tracking-[0.15em] text-slate-500 mb-2">Экипированные артефакты</h2>
          <div className="flex gap-1.5 flex-wrap">
            {mainShip.equipment.artifacts.filter(Boolean).map((equippedArt, i) => {
              const art = artifactsContent.find((a) => a.id === equippedArt!.id)
              if (!art) return null
              const tColor = tierRingColors[Math.min(art.tier - 1, 4)]
              return (
                <div
                  key={`${equippedArt!.id}-${i}`}
                  className="w-9 h-9 rounded-lg flex items-center justify-center text-[9px] font-display"
                  style={{
                    background: `${tColor}15`,
                    border: `1px solid ${tColor}30`,
                    color: tColor,
                  }}
                  title={art.name_key}
                >
                  {art.icon_path ? (
                    <img src={art.icon_path} alt={art.name_key} className="w-6 h-6 object-contain" />
                  ) : (
                    '⚙'
                  )}
                </div>
              )
            })}
          </div>
        </motion.div>
      )}

      {/* Expedition timeline */}
      {stats && stats.recent_expeditions.length > 0 && (
        <motion.div className="mb-4" variants={fadeIn} initial="hidden" animate="visible">
          <h2 className="text-[10px] font-display uppercase tracking-[0.15em] text-slate-500 mb-2">Последние экспедиции</h2>
          <div className="flex flex-col gap-1.5">
            {stats.recent_expeditions.map((exp) => (
              <div key={exp.id} className="glass-card p-2.5 flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full shrink-0 ${exp.status === 'completed' ? 'bg-neon-green' : exp.status === 'failed' ? 'bg-red-500' : 'bg-slate-600'}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] text-slate-300 truncate">{zoneName(exp.zone_config_id)}</span>
                    <span className={`text-[10px] ${exp.status === 'completed' ? 'text-neon-green' : exp.status === 'failed' ? 'text-red-400' : 'text-slate-500'}`}>
                      {exp.status === 'completed' ? 'Успех' : exp.status === 'failed' ? 'Провал' : exp.status}
                    </span>
                  </div>
                  {exp.loot_summary && (
                    <p className="text-[10px] text-slate-600 truncate mt-0.5">{readableLoot(exp.loot_summary)}</p>
                  )}
                </div>
                {exp.end_time && (
                  <span className="text-[10px] text-slate-600 shrink-0">
                    <Clock size={8} className="inline mr-0.5" />
                    {new Date(exp.end_time).toLocaleDateString()}
                  </span>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Achievements */}
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-[10px] font-display uppercase tracking-[0.15em] text-slate-500">
          Достижения
          <span className="text-slate-600 ml-1 font-mono">({claimedSet.size}/{Object.keys(ACHIEVEMENT_DEFS).length})</span>
        </h2>
        {claimableCount > 0 && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/20 font-mono">
            {claimableCount} доступно
          </span>
        )}
      </div>
      <motion.div
        className="grid grid-cols-2 gap-2"
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
      >
        {Object.entries(ACHIEVEMENT_DEFS).map(([aid, def]) => {
          const claimed = claimedSet.has(aid)
          const met = def.check(safeStats, user.daily_streak ?? 0)
          const Icon = def.icon
          const prog = def.progress?.(safeStats, user.daily_streak ?? 0)
          const canClaim = met && !claimed

          return (
            <motion.div
              key={aid}
              variants={fadeIn}
              className={`glass-card p-3 relative overflow-hidden ${
                claimed ? 'border-neon-green/20' : met ? 'border-amber-500/20' : 'opacity-50'
              }`}
            >
              <div className="flex items-start gap-2.5">
                <div className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                  claimed ? 'bg-neon-green/15 text-neon-green' : met ? 'bg-amber-500/15 text-amber-400' : 'bg-white/5 text-slate-600'
                }`}>
                  <Icon size={14} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-[10px] font-display uppercase tracking-wider ${
                    claimed ? 'text-neon-green' : met ? 'text-amber-400' : 'text-slate-500'
                  }`}>
                    {def.label}
                  </p>
                  <p className="text-[10px] text-slate-600 mt-0.5 leading-tight">{def.desc}</p>
                  {prog && !claimed && (
                    <div className="mt-1 h-1 bg-space-600 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ backgroundColor: tierRingColors[tier - 1] }}
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(100, (prog.current / prog.max) * 100)}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                      />
                    </div>
                  )}
                  {prog && !claimed && (
                    <p className="text-[10px] text-slate-600 mt-0.5">{prog.current}/{prog.max}</p>
                  )}
                </div>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-[10px] text-slate-600">{def.reward}</span>
                {canClaim && (
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleClaim(aid)}
                    disabled={claiming === aid}
                    className="text-[10px] px-3 min-h-[28px] rounded-lg bg-amber-500/15 text-amber-400 border border-amber-500/20 hover:bg-amber-500/25 transition-colors disabled:opacity-50"
                  >
                    {claiming === aid ? (
                      <motion.span animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>◌</motion.span>
                    ) : (
                      'Забрать'
                    )}
                  </motion.button>
                )}
                {claimed && (
                  <span className="text-[10px] text-neon-green/60">✓ Получено</span>
                )}
              </div>
            </motion.div>
          )
        })}
      </motion.div>

      {isAdmin && (
        <button
          onClick={() => navigate('/admin')}
          className="mt-4 w-full bg-red-600/80 text-white font-bold py-3 rounded-xl hover:bg-red-600 transition-colors"
        >
          ⚙️ Админ-панель
        </button>
      )}
    </div>
    </PullToRefresh>
  )
}

function BalanceCard({ title, value, accent, pulse, subtitle, children }: {
  title: string; value: number; accent: string; pulse?: boolean; subtitle?: React.ReactNode; children: React.ReactNode
}) {
  return (
    <motion.div
      variants={fadeIn}
      className="glass-card p-2.5 text-center relative overflow-hidden"
      style={{ borderColor: `${accent}22` }}
    >
      {pulse && (
        <motion.div
          className="absolute inset-0 opacity-[0.04]"
          style={{ background: `radial-gradient(circle at 50% 0%, ${accent}, transparent 70%)` }}
          animate={{ opacity: [0.03, 0.07, 0.03] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}
      <div className="flex justify-center mb-1">{children}</div>
      <motion.p
        className="font-display text-sm mt-0.5 tabular-nums"
        style={{ color: accent }}
        initial={{ scale: 0.5 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 15 }}
      >
        {value}
      </motion.p>
      <p className="text-[9px] text-slate-500 uppercase tracking-wider mt-0.5">{title}</p>
      {subtitle && (
        <p className="text-[8px] text-slate-500 mt-0.5">{subtitle}</p>
      )}
    </motion.div>
  )
}
