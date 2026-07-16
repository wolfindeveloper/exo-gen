import { useCallback } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { Flame, Sparkles, Gift } from 'lucide-react'
import { useGameStore } from '../store/game'

export function DailyLoginSheet() {
  const result = useGameStore((s) => s.dailyLoginResult)
  const show = useGameStore((s) => s.showDailyLoginSheet)
  const dismiss = useGameStore((s) => s.dismissDailyLoginSheet)

  const handleClose = useCallback(() => dismiss(), [dismiss])

  if (!result) return null

  const isStreakBroken = result.new_streak === 1 && result.earned_xp === 10
  const is42DayBox = result.got_box

  return (
    <AnimatePresence>
      {show && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[90] bg-black/60 backdrop-blur-sm"
            onClick={handleClose}
          />
          <motion.div
            initial={{ y: '100%', opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: '100%', opacity: 0 }}
            transition={{ type: 'spring', stiffness: 400, damping: 35 }}
            className="fixed bottom-0 left-0 right-0 z-[95] bg-space-900 border-t border-white/10 rounded-t-3xl shadow-2xl max-w-lg mx-auto"
          >
            <div className="p-6 pb-10 space-y-5">
              <div className="flex justify-center -mt-2 mb-2">
                <div className="w-10 h-1 rounded-full bg-white/20" />
              </div>

              <div className="text-center">
                <motion.div
                  initial={{ scale: 0, rotate: -30 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 15, delay: 0.1 }}
                  className="text-6xl mb-3"
                >
                  {isStreakBroken ? '🔄' : is42DayBox ? '🎁' : '☀️'}
                </motion.div>

                <h2 className="font-display text-lg text-neon-cyan uppercase tracking-[0.2em]">
                  {isStreakBroken ? 'С возвращением!' : 'Доброе утро, Капитан!'}
                </h2>

                {isStreakBroken ? (
                  <p className="text-xs text-slate-500 mt-2">
                    Стрик сброшен. Начинаем заново!
                  </p>
                ) : (
                  <p className="text-xs text-slate-500 mt-2">
                    {result.new_streak}-й день подряд в галактике
                  </p>
                )}
              </div>

              {!isStreakBroken && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                  className="glass-card p-4 flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <Flame size={24} className="text-orange-400" />
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider">Стрик</p>
                      <p className="font-display text-2xl text-orange-400 tabular-nums">
                        {result.new_streak}
                        <span className="text-sm text-slate-600 ml-1">дней</span>
                      </p>
                    </div>
                  </div>
                  {result.new_streak >= 7 && (
                    <div className="text-[9px] text-orange-400/60 text-right">
                      🔥 Горячо!
                    </div>
                  )}
                </motion.div>
              )}

              {result.earned_xp > 0 && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="glass-card p-4 flex items-center justify-between border-neon-cyan/20"
                >
                  <div className="flex items-center gap-3">
                    <Sparkles size={20} className="text-neon-cyan" />
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider">Опыт</p>
                      <p className="font-display text-sm text-slate-200">За ежедневный вход</p>
                    </div>
                  </div>
                  <span className="font-display text-xl text-neon-cyan tabular-nums">
                    +{result.earned_xp} XP
                  </span>
                </motion.div>
              )}

              {is42DayBox && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="glass-card p-4 border-amber-500/30 bg-gradient-to-br from-amber-500/5 to-purple-500/5"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <Gift size={24} className="text-amber-400" />
                    <div>
                      <p className="font-display text-sm text-amber-300 uppercase tracking-wider">
                        Бонусный бокс!
                      </p>
                      <p className="text-[10px] text-slate-500">
                        Награда за {result.new_streak} дней стрика
                      </p>
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-400 mt-2">
                    Бокс откроется автоматически после закрытия окна
                  </p>
                </motion.div>
              )}

              {!is42DayBox && result.new_streak > 0 && (
                <div className="text-center">
                  <p className="text-[9px] text-slate-600">
                    До следующего бонусного бокса:{' '}
                    <span className="text-amber-400 font-mono">
                      {42 - (result.new_streak % 42)}
                    </span>{' '}
                    дней
                  </p>
                </div>
              )}

              <button
                onClick={handleClose}
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-neon-cyan/80 to-neon-purple/80 font-display text-sm uppercase tracking-wider text-white active:scale-[0.97] transition-all"
              >
                Вперёд, к приключениям!
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
