export const statLabels: Record<string, string> = {
  speed_mod: '⚡ Скорость',
  speed: '⚡ Скорость',
  stability_bonus: '🛡️ Снижение урона',
  defense: '🛡️ Снижение урона',
  damage_reduction: '🛡️ Снижение урона',
  fuel_efficiency: '⛽ Эффективность',
  fuel: '⛽ Эффективность',
  capacity: '📦 Ёмкость',
  luck: '🍀 Удача',
  repair: '🔧 Ремонт',
  xp: '⭐ Опыт',
  fragment: '📜 Фрагменты',
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
  xp: '⭐',
  fragment: '📜',
}

export function formatBonus(v: unknown): string {
  if (typeof v === 'number') return `${v > 0 ? '+' : ''}${(v * 100).toFixed(0)}%`
  return String(v)
}
