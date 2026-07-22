import type { InventoryItem } from '../types'

export function isFuel(item: InventoryItem['item']): boolean {
  if (item.type !== 'consumable') return false
  const effect = item.effect as Record<string, unknown>
  return typeof effect?.restore_tea === 'number' && (effect.restore_tea as number) > 0
}

export function isRepairKit(item: InventoryItem['item']): boolean {
  if (item.type !== 'consumable') return false
  const effect = item.effect as Record<string, unknown>
  return typeof effect?.restore_optimism === 'number' && (effect.restore_optimism as number) > 0
}

export function countFuel(inventory: InventoryItem[]): number {
  return inventory.filter((i) => isFuel(i.item)).reduce((sum, i) => sum + i.quantity, 0)
}

export function countRepairKits(inventory: InventoryItem[]): number {
  return inventory.filter((i) => isRepairKit(i.item)).reduce((sum, i) => sum + i.quantity, 0)
}
