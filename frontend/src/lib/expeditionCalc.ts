export interface CalculatedStats {
  effectiveRisk: number
  effectiveFuelCost: number
  effectiveDuration: number
  fuelOk: boolean
  estimatedMaxDamage: number
  riskPercent: number
  durationHours: number
}

export interface ArtifactBonus {
  speed_mod?: number
  damage_reduction?: number
  fuel_efficiency?: number
}

export function calculateZoneStats(
  zoneRiskFactor: number,
  zoneFuelCost: number,
  zoneDurationHours: number,
  shipStability: number,
  shipSpeedMod: number,
  shipFuelCurrent: number,
  artifactBonuses: ArtifactBonus[] = [],
): CalculatedStats {
  const totalSpeedBonus = artifactBonuses.reduce((s, a) => s + (a.speed_mod || 0), 0)
  const totalDamageReduction = artifactBonuses.reduce((s, a) => s + (a.damage_reduction || 0), 0)
  const totalFuelEfficiency = artifactBonuses.reduce((s, a) => s + (a.fuel_efficiency || 0), 0)

  const effectiveRisk = Math.max(0, zoneRiskFactor - totalDamageReduction)
  const effectiveFuelCost = zoneFuelCost * (1 - totalFuelEfficiency)
  const effectiveDuration = zoneDurationHours / shipSpeedMod * (1 - totalSpeedBonus)

  return {
    effectiveRisk,
    effectiveFuelCost: Math.max(0, Math.round(effectiveFuelCost)),
    effectiveDuration: Math.max(0.5, effectiveDuration),
    fuelOk: shipFuelCurrent >= Math.max(0, Math.round(effectiveFuelCost)),
    estimatedMaxDamage: shipStability > 0
      ? Math.round((effectiveRisk / (shipStability / 100)) * 100 * 10) / 10
      : 0,
    riskPercent: Math.min(100, Math.round(effectiveRisk * 100)),
    durationHours: Math.round(effectiveDuration * 10) / 10,
  }
}
