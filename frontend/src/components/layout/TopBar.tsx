import { memo, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Coins, User, Settings } from 'lucide-react'
import { usePlayerStore } from '../../store/usePlayerStore'
import { useI18n } from '../../hooks/useI18n'

const RANKS: Record<number, string> = {
  1: 'rank.scout',
  2: 'rank.strider',
  3: 'rank.vector',
  4: 'rank.archon',
  5: 'rank.genesis',
}

const TIER_TO_RARITY: Record<number, string> = {
  1: 'from-gray-500 to-gray-600',
  2: 'from-green-500 to-green-600',
  3: 'from-blue-500 to-blue-600',
  4: 'from-purple-500 to-purple-600',
  5: 'from-yellow-500 to-yellow-600',
}

const MOCK_PLAYER = {
  username: 'Навигатор',
  tier: 1,
  level: 5,
  xp: 420,
  xgen_balance: 12450,
}

interface TopBarProps {
  onSettingsClick?: () => void
}

/**
 * Вызывает тактильную отдачу через Telegram WebApp SDK.
 * Если SDK недоступен — ничего не делает.
 */
function hapticFeedback(type: 'light' | 'medium' | 'heavy' | 'success' | 'error' | 'warning'): void {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const WebApp = (window as any).Telegram?.WebApp
    if (WebApp?.HapticFeedback) {
      const hf = WebApp.HapticFeedback
      if (type === 'success' && hf.notificationOccurred) {
        hf.notificationOccurred('success')
      } else if (type === 'error' && hf.notificationOccurred) {
        hf.notificationOccurred('error')
      } else if (type === 'warning' && hf.notificationOccurred) {
        hf.notificationOccurred('warning')
      } else if (hf.impactOccurred) {
        hf.impactOccurred(type)
      }
    }
  } catch {
    // Игнорируем ошибки — тактильная отдача не критична
  }
}

const TopBar = memo(({ onSettingsClick }: TopBarProps) => {
  const { player, isLoading, error } = usePlayerStore()
  const { t } = useI18n()
  const prevXgenRef = useRef<number>(player?.xgen_balance ?? 0)
  const prevXpRef = useRef<number>(player?.xp ?? 0)

  // Безопасное получение данных с фоллбэками
  const data = player || MOCK_PLAYER
  const xgenBalance = typeof data.xgen_balance === 'number' ? data.xgen_balance : 0
  const xp = typeof data.xp === 'number' ? data.xp : 0
  const level = typeof data.level === 'number' ? data.level : 1
  const tier = typeof data.tier === 'number' ? data.tier : 1
  const username = data.username || MOCK_PLAYER.username

  const rarityGradient = TIER_TO_RARITY[tier] || TIER_TO_RARITY[1]
  const rank = RANKS[tier] || 'rank.scout'
  const xpForNextLevel = Math.floor(100 * Math.pow(level + 1, 1.8))
  const xpForCurrentLevel = Math.floor(100 * Math.pow(level, 1.8))
  const xpProgress = xpForNextLevel !== xpForCurrentLevel
    ? ((xp - xpForCurrentLevel) / (xpForNextLevel - xpForCurrentLevel)) * 100
    : 0

  /** Тактильная отдача при изменении XGEN или XP */
  useEffect(() => {
    if (!player) return

    const currentXgen = player.xgen_balance ?? 0
    const currentXp = player.xp ?? 0

    if (currentXgen !== prevXgenRef.current) {
      const diff = currentXgen - prevXgenRef.current
      hapticFeedback(diff > 0 ? 'success' : 'error')
      prevXgenRef.current = currentXgen
    }

    if (currentXp !== prevXpRef.current) {
      hapticFeedback('light')
      prevXpRef.current = currentXp
    }
  }, [player, player?.xgen_balance, player?.xp])

  if (isLoading && !player) {
    return (
      <header
        className="fixed top-0 left-0 right-0 z-50 px-3 bg-cosmic-bg/90 backdrop-blur-md border-b border-cosmic-border"
        style={{ paddingTop: 'max(10px, env(safe-area-inset-top))' }}
      >
        <div className="flex items-center justify-center max-w-lg mx-auto h-12">
          <span className="text-xs text-gray-500 animate-pulse">{t('topbar.loading')}</span>
        </div>
      </header>
    )
  }

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 px-3 bg-cosmic-bg/90 backdrop-blur-md border-b border-cosmic-border"
      style={{ paddingTop: 'max(10px, env(safe-area-inset-top))' }}
    >
      <div className="flex items-center justify-between gap-3 max-w-lg mx-auto">
        {/* Аватар + Имя + Ранг */}
        <div className="flex items-center gap-2.5">
          <motion.div
            className="relative"
            animate={{
              boxShadow: [
                '0 0 10px 2px rgba(6, 182, 212, 0.4)',
                '0 0 15px 4px rgba(6, 182, 212, 0.6)',
                '0 0 10px 2px rgba(6, 182, 212, 0.4)',
              ],
            }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            style={{ borderRadius: '50%' }}
          >
            <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${rarityGradient} p-0.5`}>
              <div className="w-full h-full rounded-full bg-cosmic-bg flex items-center justify-center">
                <User className="w-4 h-4 text-neon-cyan" />
              </div>
            </div>
          </motion.div>
          <div>
            <p className="text-[11px] text-gray-300 leading-tight">
              {t('topbar.navigator')}: <span className="text-white font-semibold">{username}</span>
            </p>
            <p className="text-[10px] text-gray-500 leading-tight">
              {t('topbar.rank')}: <span className="text-neon-purple font-medium">{t(rank as any)}</span>
            </p>
          </div>
        </div>

        {/* XGEN + Настройки */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-black/40 backdrop-blur-sm border border-yellow-400/30 rounded-full px-2.5 py-1">
            <motion.div
              animate={{ rotate: [0, 10, -10, 0], scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            >
              <Coins className="w-3.5 h-3.5 text-yellow-400" />
            </motion.div>
            <span className="text-xs font-bold text-yellow-400">{xgenBalance.toLocaleString()}</span>
          </div>

          {/* Кнопка настроек: min 44px touch target */}
          <button
            onClick={() => {
              hapticFeedback('light')
              onSettingsClick?.()
            }}
            className="min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-cosmic-cardHover transition-colors"
            aria-label={t('topbar.settings')}
          >
            <Settings className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {/* XP-бар */}
      <div className="max-w-lg mx-auto mt-2">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold text-neon-cyan tracking-wider">{t('topbar.level')} {level}</span>
          <div className="flex-1 h-1.5 bg-black/60 rounded-full overflow-hidden border border-neon-cyan/20">
            <motion.div
              className="h-full rounded-full"
              style={{
                background: 'linear-gradient(90deg, #06B6D4, #A855F7, #06B6D4)',
                backgroundSize: '200% 100%',
              }}
              initial={{ width: 0 }}
              animate={{
                width: `${Math.min(100, Math.max(0, xpProgress))}%`,
                backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
              }}
              transition={{
                width: { duration: 1, ease: 'easeOut' },
                backgroundPosition: { duration: 3, repeat: Infinity, ease: 'linear' },
              }}
            />
          </div>
          <span className="text-[10px] font-bold text-neon-purple tracking-wider">
            {t('topbar.xp')}: {xp}
          </span>
        </div>
      </div>
    </header>
  )
})

TopBar.displayName = 'TopBar'
export default TopBar
