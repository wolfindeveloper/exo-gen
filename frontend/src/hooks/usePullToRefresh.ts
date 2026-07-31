import { useCallback, useRef, useState } from 'react'

const THRESHOLD = 80
const MAX_PULL = 120

export function usePullToRefresh(onRefresh: () => Promise<void> | void) {
  const [pullDistance, setPullDistance] = useState(0)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const touching = useRef(false)
  const startY = useRef(0)

  const onTouchStart = useCallback((e: React.TouchEvent) => {
    if (isRefreshing) return
    const scrollY = window.scrollY || document.documentElement.scrollTop
    if (scrollY > 0) return
    touching.current = true
    startY.current = e.touches[0].clientY
  }, [isRefreshing])

  const onTouchMove = useCallback((e: React.TouchEvent) => {
    if (!touching.current || isRefreshing) return
    const delta = e.touches[0].clientY - startY.current
    if (delta < 0) {
      setPullDistance(0)
      return
    }
    const distance = Math.min(delta * 0.5, MAX_PULL)
    setPullDistance(distance)
  }, [isRefreshing])

  const onTouchEnd = useCallback(async () => {
    if (!touching.current) return
    touching.current = false

    if (pullDistance >= THRESHOLD && !isRefreshing) {
      setIsRefreshing(true)
      setPullDistance(THRESHOLD)
      try {
        await onRefresh()
      } finally {
        setIsRefreshing(false)
        setPullDistance(0)
      }
    } else {
      setPullDistance(0)
    }
  }, [pullDistance, isRefreshing, onRefresh])

  const progress = Math.min(pullDistance / THRESHOLD, 1)

  return {
    pullDistance,
    isRefreshing,
    progress,
    handlers: {
      onTouchStart,
      onTouchMove,
      onTouchEnd,
    },
  }
}
