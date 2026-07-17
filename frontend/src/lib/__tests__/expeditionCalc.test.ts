import { describe, it, expect } from 'vitest'
import { calculateZoneStats } from '../expeditionCalc'

describe('calculateZoneStats', () => {
  it('baseline — no artifacts, risk 0.1, optimism 100', () => {
    const result = calculateZoneStats(0.1, 10, 4, 100, 1.2, 100)
    expect(result.effectiveRisk).toBeCloseTo(0.1)
    expect(result.estimatedMaxDamage).toBe(10)
    expect(result.riskPercent).toBe(10)
    expect(result.fuelOk).toBe(true)
  })

  it('high risk zone (0.5), optimism 100, no defense', () => {
    const result = calculateZoneStats(0.5, 20, 8, 100, 1.0, 200)
    expect(result.effectiveRisk).toBeCloseTo(0.5)
    expect(result.estimatedMaxDamage).toBe(50)
    expect(result.riskPercent).toBe(50)
  })

  it('defense reduces damage correctly (matches backend)', () => {
    const bonuses = [{ damage_reduction: 0.2 }]
    const result = calculateZoneStats(0.5, 10, 4, 100, 1.0, 100, bonuses)
    expect(result.effectiveRisk).toBeCloseTo(0.3)
    expect(result.estimatedMaxDamage).toBe(30)
    expect(result.riskPercent).toBe(30)
  })

  it('defense fully negates risk → 0 damage', () => {
    const bonuses = [{ damage_reduction: 0.15 }]
    const result = calculateZoneStats(0.1, 10, 4, 100, 1.0, 100, bonuses)
    expect(result.effectiveRisk).toBe(0)
    expect(result.estimatedMaxDamage).toBe(0)
    expect(result.riskPercent).toBe(0)
  })

  it('low optimism ship takes more relative damage', () => {
    const result = calculateZoneStats(0.1, 10, 4, 50, 1.0, 100)
    expect(result.estimatedMaxDamage).toBe(20)
  })

  it('artifact speed bonus reduces duration', () => {
    const bonuses = [{ speed_mod: 0.2 }]
    const result = calculateZoneStats(0.1, 10, 4, 100, 1.0, 100, bonuses)
    expect(result.effectiveDuration).toBeLessThan(4)
  })

  it('artifact fuel efficiency reduces fuel cost', () => {
    const bonuses = [{ fuel_efficiency: 0.2 }]
    const result = calculateZoneStats(0.1, 10, 4, 100, 1.0, 100, bonuses)
    expect(result.effectiveFuelCost).toBe(8)
  })

  it('insufficient fuel → fuelOk is false', () => {
    const result = calculateZoneStats(0.1, 15, 4, 100, 1.0, 10)
    expect(result.fuelOk).toBe(false)
  })
})
