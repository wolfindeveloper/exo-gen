import { describe, it, expect } from 'vitest'
import { isFuel, isRepairKit, countFuel } from '../items'
import type { InventoryItem } from '../../types'

function makeItem(id: string, type: string, effect: Record<string, unknown>): InventoryItem {
  return {
    item: { id, name: '', description: '', type, rarity: 'common', effect, is_tradable: false, sell_price: 0 },
    quantity: 1,
  }
}

describe('isFuel', () => {
  it('returns true for consumable with restore_tea', () => {
    expect(isFuel(makeItem('f1', 'consumable', { restore_tea: 50 }).item)).toBe(true)
  })
  it('returns false for artifact', () => {
    expect(isFuel(makeItem('a1', 'artifact', { bonus_speed: 0.1 }).item)).toBe(false)
  })
  it('returns false for consumable without restore_tea', () => {
    expect(isFuel(makeItem('r1', 'consumable', { restore_optimism: 30 }).item)).toBe(false)
  })
  it('returns false for restore_tea = 0', () => {
    expect(isFuel(makeItem('f0', 'consumable', { restore_tea: 0 }).item)).toBe(false)
  })
})

describe('isRepairKit', () => {
  it('returns true for consumable with restore_optimism', () => {
    expect(isRepairKit(makeItem('r1', 'consumable', { restore_optimism: 30 }).item)).toBe(true)
  })
  it('returns false for fuel', () => {
    expect(isRepairKit(makeItem('f1', 'consumable', { restore_tea: 50 }).item)).toBe(false)
  })
})

describe('countFuel', () => {
  it('sums quantities of fuel items', () => {
    const inv = [
      makeItem('f1', 'consumable', { restore_tea: 20 }),
      makeItem('f2', 'consumable', { restore_tea: 50 }),
      makeItem('r1', 'consumable', { restore_optimism: 30 }),
    ]
    inv[0].quantity = 3
    inv[1].quantity = 2
    expect(countFuel(inv)).toBe(5)
  })
  it('returns 0 for empty inventory', () => {
    expect(countFuel([])).toBe(0)
  })
})
