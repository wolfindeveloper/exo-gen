import { describe, it, expect } from 'vitest'
import {
  calculateLevel,
  getMaxArtifactSlots,
  canAccessZone,
  getNextSlotUnlock,
  getUnlockedTiers,
} from '../progression'

describe('calculateLevel', () => {
  it('returns 1 for 0 xp', () => expect(calculateLevel(0)).toBe(1))
  it('returns 1 for negative xp', () => expect(calculateLevel(-100)).toBe(1))
  it('level boundaries', () => {
    expect(calculateLevel(999)).toBe(1)
    expect(calculateLevel(1000)).toBe(1)
    expect(calculateLevel(1999)).toBe(1)
    expect(calculateLevel(2000)).toBe(2)
    expect(calculateLevel(25000)).toBe(25)
  })
})

describe('getMaxArtifactSlots', () => {
  it('level 1 → 4 slots', () => expect(getMaxArtifactSlots(1)).toBe(4))
  it('level 5 → 6 slots', () => expect(getMaxArtifactSlots(5)).toBe(6))
  it('level 15 → 8 slots', () => expect(getMaxArtifactSlots(15)).toBe(8))
  it('level 100 → 8 slots', () => expect(getMaxArtifactSlots(100)).toBe(8))
})

describe('canAccessZone', () => {
  it('level 1 can access T1', () => {
    const r = canAccessZone(1, 1)
    expect(r.isUnlocked).toBe(true)
  })
  it('level 1 cannot access T2', () => {
    const r = canAccessZone(1, 2)
    expect(r.isUnlocked).toBe(false)
    expect(r.requiredLevel).toBe(3)
  })
  it('level 25 can access T5', () => {
    expect(canAccessZone(25, 5).isUnlocked).toBe(true)
  })
})

describe('getNextSlotUnlock', () => {
  it('for new player → level 5', () => {
    expect(getNextSlotUnlock(1)).toEqual({ requiredLevel: 5, newSlotCount: 6 })
  })
  it('for level 6 → level 15', () => {
    expect(getNextSlotUnlock(6)).toEqual({ requiredLevel: 15, newSlotCount: 8 })
  })
  it('for level 20 → null', () => {
    expect(getNextSlotUnlock(20)).toBeNull()
  })
})

describe('getUnlockedTiers', () => {
  it('level 1 → [1]', () => expect(getUnlockedTiers(1)).toEqual([1]))
  it('level 10 → [1, 2, 3]', () => expect(getUnlockedTiers(10)).toEqual([1, 2, 3]))
  it('level 30 → all tiers', () => expect(getUnlockedTiers(30)).toEqual([1, 2, 3, 4, 5]))
})
