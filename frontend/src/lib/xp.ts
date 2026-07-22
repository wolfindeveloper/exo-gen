const XP_PER_LEVEL = 1000

export function calculateLevel(xp: number): number {
  if (xp < 0) return 1
  return 1 + Math.floor(xp / XP_PER_LEVEL)
}

export function getNextLevelXp(level: number): number {
  return level * XP_PER_LEVEL
}

export function getXpProgress(xp: number, level: number): number {
  const xpForCurrentLevel = (level - 1) * XP_PER_LEVEL
  const xpInLevel = xp - xpForCurrentLevel
  return Math.min(100, Math.max(0, Math.round((xpInLevel / XP_PER_LEVEL) * 100)))
}

export function getXpToNextLevel(xp: number, level: number): number {
  const nextLevelXp = getNextLevelXp(level)
  return Math.max(0, nextLevelXp - xp)
}
