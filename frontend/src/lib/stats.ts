export const statLabels: Record<string, string> = {
  speed_mod: 'Скорость',
  speed: 'Скорость',
  stability_bonus: 'Снижение урона',
  defense: 'Защита',
  damage_reduction: 'Снижение урона',
  fuel_efficiency: 'Экономия топлива',
  fuel: 'Экономия топлива',
  capacity: 'Ёмкость бака',
  luck: 'Удача',
  repair: 'Ремонт',
  repair_bonus: 'Ремонт',
  xp: 'Опыт',
  fragment: 'Фрагменты',
  bonus_speed: 'Скорость',
  bonus_defense: 'Защита',
  bonus_capacity: 'Ёмкость бака',
  bonus_luck: 'Удача',
  bonus_fuel: 'Экономия топлива',
  bonus_repair: 'Ремонт',
  bonus_xp: 'Опыт',
  bonus_fragment: 'Фрагменты',
}

export const statIcons: Record<string, string> = {
  speed_mod: '⚡',
  speed: '⚡',
  stability_bonus: '🛡️',
  defense: '🛡️',
  damage_reduction: '🛡️',
  fuel_efficiency: '⛽',
  fuel: '⛽',
  capacity: '📦',
  luck: '🍀',
  repair: '🔧',
  repair_bonus: '🔧',
  xp: '⭐',
  fragment: '📜',
  bonus_speed: '⚡',
  bonus_defense: '🛡️',
  bonus_capacity: '📦',
  bonus_luck: '🍀',
  bonus_fuel: '⛽',
  bonus_repair: '🔧',
  bonus_xp: '⭐',
  bonus_fragment: '📜',
}

export function formatBonus(v: unknown): string {
  if (typeof v === 'number') return `${v > 0 ? '+' : ''}${(v * 100).toFixed(0)}%`
  return String(v)
}

export function getArtifactMainIcon(modifiers: Record<string, number> | undefined): string {
  if (!modifiers) return '⚙'
  const bonusEntries = Object.entries(modifiers).filter(
    ([k, v]) => k.startsWith('bonus_') && typeof v === 'number' && v !== 0,
  )
  if (bonusEntries.length === 0) return '⚙'
  const [mainKey] = bonusEntries.reduce((best, cur) =>
    Math.abs(cur[1] as number) > Math.abs(best[1] as number) ? cur : best,
  )
  return statIcons[mainKey] || '⚙'
}
