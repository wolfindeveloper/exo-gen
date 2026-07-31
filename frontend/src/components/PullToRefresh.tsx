import { type ReactNode, useCallback, useEffect, useRef } from 'react'
import { motion } from 'motion/react'

import { usePullToRefresh } from '../hooks/usePullToRefresh'
import { hapticImpact } from '../lib/telegram'

interface PullToRefreshProps {
  onRefresh: () => Promise<void> | void
  children: ReactNode
}

export function PullToRefresh({ onRefresh, children }: PullToRefreshProps) {
  const prevProgress = useRef(0)

  const wrappedRefresh = useCallback(async () => {
    hapticImpact('medium')
    await onRefresh()
    hapticImpact('medium')
  }, [onRefresh])

  const { pullDistance, isRefreshing, progress, handlers } = usePullToRefresh(wrappedRefresh)

  useEffect(() => {
    if (progress >= 1 && prevProgress.current < 1) {
      hapticImpact('light')
    }
    prevProgress.current = progress
  }, [progress])

  return (
    <div {...handlers} className="relative select-none">
      {/* Indicator */}
      <div
        className="fixed top-0 left-1/2 -translate-x-1/2 z-50 flex items-center justify-center pointer-events-none"
        style={{
          transform: `translateX(-50%) translateY(${pullDistance > 0 ? pullDistance - 40 : -60}px)`,
          opacity: progress,
          transition: isRefreshing ? 'none' : 'transform 0.2s ease-out, opacity 0.2s ease-out',
        }}
      >
        <motion.div
          animate={isRefreshing ? { rotate: 360 } : { rotate: progress * 360 }}
          transition={isRefreshing ? { repeat: Infinity, duration: 1, ease: 'linear' } : { duration: 0 }}
          className="text-2xl"
        >
          {progress >= 1 && !isRefreshing ? '🎖️' : '🚀'}
        </motion.div>
      </div>

      {/* Content */}
      <div
        style={{
          transform: pullDistance > 0 ? `translateY(${pullDistance * 0.3}px)` : undefined,
          transition: isRefreshing ? 'none' : 'transform 0.2s ease-out',
        }}
      >
        {children}
      </div>
    </div>
  )
}
