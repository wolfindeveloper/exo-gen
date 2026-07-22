import { describe, it, expect } from 'vitest'
import { calculateLevel, getXpProgress, getXpToNextLevel } from '../xp'

describe('calculateLevel', () => {
  it('level 1 for 0 xp', () => expect(calculateLevel(0)).toBe(1))
  it('level 1 for 999 xp', () => expect(calculateLevel(999)).toBe(1))
  it('level 2 for 1000 xp', () => expect(calculateLevel(1000)).toBe(2))
  it('level 2 for 1999 xp', () => expect(calculateLevel(1999)).toBe(2))
  it('level 3 for 2000 xp', () => expect(calculateLevel(2000)).toBe(3))
  it('level 1 for negative xp', () => expect(calculateLevel(-100)).toBe(1))
})

describe('getXpProgress', () => {
  it('0% at start of level', () => expect(getXpProgress(0, 1)).toBe(0))
  it('50% at mid level', () => expect(getXpProgress(500, 1)).toBe(50))
  it('100% at end of level', () => expect(getXpProgress(999, 1)).toBe(100))
  it('0% at start of level 2', () => expect(getXpProgress(1000, 2)).toBe(0))
  it('50% at mid level 2', () => expect(getXpProgress(1500, 2)).toBe(50))
})

describe('getXpToNextLevel', () => {
  it('1000 to next for level 1 with 0 xp', () => expect(getXpToNextLevel(0, 1)).toBe(1000))
  it('500 to next for level 1 with 500 xp', () => expect(getXpToNextLevel(500, 1)).toBe(500))
  it('0 to next for level 1 with 1000 xp', () => expect(getXpToNextLevel(1000, 1)).toBe(0))
  it('1000 to next for level 2 with 1000 xp', () => expect(getXpToNextLevel(1000, 2)).toBe(1000))
})
