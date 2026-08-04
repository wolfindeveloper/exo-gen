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
