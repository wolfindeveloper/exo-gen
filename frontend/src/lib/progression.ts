/**
 * Правила прогрессии игрока. Зеркалит backend LevelProgressionService.
 * Единый источник истины для UI: разблокировки зон и слотов.
 */

// ── Таблица разблокировок зон ───────────────────────────────────
export const ZONE_UNLOCK_TABLE: Record<number, number> = {
  1: 1,   // T1: доступна сразу
  2: 3,   // T2: уровень 3
  3: 8,   // T3: уровень 8
  4: 12,  // T4: уровень 12
  5: 25,  // T5: уровень 25
}

// ── Таблица разблокировок слотов артефактов ─────────────────────
// [required_level, total_slots]
export const SLOT_UNLOCK_TABLE: [number, number][] = [
  [1,  4],
  [5,  6],
  [15, 8],
]

export const XP_PER_LEVEL = 1000

// ── Вычисления ──────────────────────────────────────────────────

export function calculateLevel(xp: number): number {
  if (xp < 0) return 1
  return Math.max(1, Math.floor(xp / XP_PER_LEVEL))
}

export function getMaxArtifactSlots(playerLevel: number): number {
  let maxSlots = SLOT_UNLOCK_TABLE[0][1]
  for (const [levelThreshold, slots] of SLOT_UNLOCK_TABLE) {
    if (playerLevel >= levelThreshold) {
      maxSlots = slots
    } else {
      break
    }
  }
  return maxSlots
}

export function getNextSlotUnlock(playerLevel: number): { requiredLevel: number; newSlotCount: number } | null {
  for (const [levelThreshold, slots] of SLOT_UNLOCK_TABLE) {
    if (playerLevel < levelThreshold) {
      return { requiredLevel: levelThreshold, newSlotCount: slots }
    }
  }
  return null
}

export function canAccessZone(playerLevel: number, zoneTier: number): {
  isUnlocked: boolean
  requiredLevel: number | null
} {
  const required = ZONE_UNLOCK_TABLE[zoneTier] ?? 1
  if (playerLevel >= required) {
    return { isUnlocked: true, requiredLevel: null }
  }
  return { isUnlocked: false, requiredLevel: required }
}

export function getNextZoneUnlock(playerLevel: number): { requiredLevel: number; tier: number } | null {
  const tiers = Object.keys(ZONE_UNLOCK_TABLE).map(Number).sort((a, b) => a - b)
  for (const tier of tiers) {
    const required = ZONE_UNLOCK_TABLE[tier]
    if (playerLevel < required) {
      return { requiredLevel: required, tier }
    }
  }
  return null
}

export function getUnlockedTiers(playerLevel: number): number[] {
  return Object.entries(ZONE_UNLOCK_TABLE)
    .filter(([_, req]) => playerLevel >= req)
    .map(([tier]) => Number(tier))
}

// ── UI helpers ──────────────────────────────────────────────────

export function formatUnlockHint(requiredLevel: number, currentLevel: number): string {
  const diff = requiredLevel - currentLevel
  if (diff <= 1) return 'Следующий уровень!'
  return `Ещё ${diff} ${diff === 2 || diff === 3 || diff === 4 ? 'уровня' : 'уровней'}`
}
