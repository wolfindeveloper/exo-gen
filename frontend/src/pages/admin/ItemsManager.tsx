import { useCallback, useEffect, useState } from 'react'
import { Pencil, Plus, Trash2, X } from 'lucide-react'

import { api } from '../../api/client'
import type { AdminItem, CreateItemPayload, ItemRarity, ItemType, UpdateItemPayload } from '../../types'

const ITEM_TYPES: ItemType[] = ['consumable', 'artifact', 'material', 'key_item', 'loot_box']
const RARITIES: ItemRarity[] = ['common', 'uncommon', 'rare', 'epic', 'legendary']

const RARITY_COLORS: Record<string, string> = {
  common: 'text-gray-400',
  uncommon: 'text-green-400',
  rare: 'text-blue-400',
  epic: 'text-purple-400',
  legendary: 'text-amber-400',
}

const TYPE_LABELS: Record<string, string> = {
  consumable: 'Расходник',
  artifact: 'Артефакт',
  material: 'Материал',
  key_item: 'Ключевой предмет',
  loot_box: 'Лутбокс',
}

interface FormState {
  name: string
  description: string
  type: ItemType
  rarity: ItemRarity
  is_tradable: boolean
  sell_price: string
  restore_tea: string
  restore_optimism: string
  bonus_speed: string
  bonus_defense: string
  bonus_capacity: string
  bonus_luck: string
  bonus_fuel: string
  bonus_repair: string
  bonus_xp: string
  bonus_fragment: string
}

const EMPTY_FORM: FormState = {
  name: '',
  description: '',
  type: 'consumable',
  rarity: 'common',
  is_tradable: false,
  sell_price: '0',
  restore_tea: '',
  restore_optimism: '',
  bonus_speed: '',
  bonus_defense: '',
  bonus_capacity: '',
  bonus_luck: '',
  bonus_fuel: '',
  bonus_repair: '',
  bonus_xp: '',
  bonus_fragment: '',
}

function numOrNull(val: string): number | null {
  const n = parseFloat(val)
  return isNaN(n) ? null : n
}

function buildEffect(form: FormState): Record<string, unknown> {
  if (form.type === 'consumable') {
    const effect: Record<string, unknown> = {}
    const rt = numOrNull(form.restore_tea)
    const ro = numOrNull(form.restore_optimism)
    if (rt !== null) effect.restore_tea = rt
    if (ro !== null) effect.restore_optimism = ro
    return effect
  }
  if (form.type === 'artifact') {
    const effect: Record<string, unknown> = {}
    const fields: [keyof FormState, string][] = [
      ['bonus_speed', 'bonus_speed'],
      ['bonus_defense', 'bonus_defense'],
      ['bonus_capacity', 'bonus_capacity'],
      ['bonus_luck', 'bonus_luck'],
      ['bonus_fuel', 'bonus_fuel'],
      ['bonus_repair', 'bonus_repair'],
      ['bonus_xp', 'bonus_xp'],
      ['bonus_fragment', 'bonus_fragment'],
    ]
    for (const [, backendKey] of fields) {
      const val = numOrNull(form[backendKey as keyof FormState] as string)
      if (val !== null) effect[backendKey] = val
    }
    return effect
  }
  return { restore_tea: 0 }
}

function formFromItem(item: AdminItem): FormState {
  const e = item.effect as Record<string, unknown>
  return {
    name: item.name,
    description: item.description,
    type: item.type,
    rarity: item.rarity,
    is_tradable: item.is_tradable,
    sell_price: String(item.sell_price),
    restore_tea: e.restore_tea != null ? String(e.restore_tea) : '',
    restore_optimism: e.restore_optimism != null ? String(e.restore_optimism) : '',
    bonus_speed: e.bonus_speed != null ? String(e.bonus_speed) : '',
    bonus_defense: e.bonus_defense != null ? String(e.bonus_defense) : '',
    bonus_capacity: e.bonus_capacity != null ? String(e.bonus_capacity) : '',
    bonus_luck: e.bonus_luck != null ? String(e.bonus_luck) : '',
    bonus_fuel: e.bonus_fuel != null ? String(e.bonus_fuel) : '',
    bonus_repair: e.bonus_repair != null ? String(e.bonus_repair) : '',
    bonus_xp: e.bonus_xp != null ? String(e.bonus_xp) : '',
    bonus_fragment: e.bonus_fragment != null ? String(e.bonus_fragment) : '',
  }
}

const CONSUMABLE_FIELDS: { key: keyof FormState; label: string }[] = [
  { key: 'restore_tea', label: 'Восстановление чая (restore_tea)' },
  { key: 'restore_optimism', label: 'Восстановление оптимизма (restore_optimism)' },
]

const ARTIFACT_FIELDS: { key: keyof FormState; label: string }[] = [
  { key: 'bonus_speed', label: 'Бонус скорости (bonus_speed)' },
  { key: 'bonus_defense', label: 'Бонус защиты (bonus_defense)' },
  { key: 'bonus_capacity', label: 'Бонус вместимости (bonus_capacity)' },
  { key: 'bonus_luck', label: 'Бонус удачи (bonus_luck)' },
  { key: 'bonus_fuel', label: 'Бонус топлива (bonus_fuel)' },
  { key: 'bonus_repair', label: 'Бонус ремонта (bonus_repair)' },
  { key: 'bonus_xp', label: 'Бонус опыта (bonus_xp)' },
  { key: 'bonus_fragment', label: 'Бонус фрагментов (bonus_fragment)' },
]

export function ItemsManager() {
  const [items, setItems] = useState<AdminItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [forbidden, setForbidden] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editingItem, setEditingItem] = useState<AdminItem | null>(null)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  const loadItems = useCallback(async () => {
    try {
      setLoading(true)
      setForbidden(false)
      setError(null)
      const data = await api.getAdminItems()
      setItems(data.items)
    } catch (e) {
      const err = e as Error & { status?: number }
      if (err.status === 403 || err.message.includes('Access denied')) {
        setForbidden(true)
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadItems()
  }, [loadItems])

  const openCreate = () => {
    setEditingItem(null)
    setForm(EMPTY_FORM)
    setShowForm(true)
  }

  const openEdit = (item: AdminItem) => {
    setEditingItem(item)
    setForm(formFromItem(item))
    setShowForm(true)
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingItem(null)
    setForm(EMPTY_FORM)
  }

  const handleSubmit = async () => {
    if (!form.name.trim() || !form.description.trim()) {
      setError('Имя и описание обязательны')
      return
    }
    try {
      setSubmitting(true)
      setError(null)
      const effect = buildEffect(form)
      if (editingItem) {
        const payload: UpdateItemPayload = {
          name: form.name,
          description: form.description,
          rarity: form.rarity,
          effect,
          is_tradable: form.is_tradable,
          sell_price: parseInt(form.sell_price) || 0,
        }
        await api.updateAdminItem(editingItem.id, payload)
      } else {
        const payload: CreateItemPayload = {
          name: form.name,
          description: form.description,
          type: form.type,
          rarity: form.rarity,
          effect,
          is_tradable: form.is_tradable,
          sell_price: parseInt(form.sell_price) || 0,
        }
        await api.createAdminItem(payload)
      }
      closeForm()
      await loadItems()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      setDeleting(true)
      await api.deleteAdminItem(deleteId)
      setDeleteId(null)
      await loadItems()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setDeleting(false)
    }
  }

  if (forbidden) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-2xl mb-2">🔒</p>
          <p className="text-red-400 text-lg font-medium">Доступ запрещен. Вы не являетесь администратором.</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400 animate-pulse">Загрузка предметов...</p>
      </div>
    )
  }

  const effectFields = form.type === 'consumable' ? CONSUMABLE_FIELDS : form.type === 'artifact' ? ARTIFACT_FIELDS : []

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Предметы</h2>
          <p className="text-sm text-gray-500">Всего: {items.length}</p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors"
        >
          <Plus size={18} />
          Создать предмет
        </button>
      </div>

      {error && (
        <div className="mb-4 bg-red-900/30 border border-red-700/50 text-red-300 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {items.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-500">
          Предметов пока нет. Создайте первый!
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-750 border-b border-gray-700 text-left text-gray-400">
                <th className="px-4 py-3 font-medium">Имя</th>
                <th className="px-4 py-3 font-medium">Тип</th>
                <th className="px-4 py-3 font-medium">Редкость</th>
                <th className="px-4 py-3 font-medium">Цена продажи</th>
                <th className="px-4 py-3 font-medium">Статус</th>
                <th className="px-4 py-3 font-medium text-right">Действия</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                  <td className="px-4 py-3 font-medium text-white">{item.name}</td>
                  <td className="px-4 py-3 text-gray-400">{TYPE_LABELS[item.type] || item.type}</td>
                  <td className={`px-4 py-3 font-medium ${RARITY_COLORS[item.rarity] || 'text-gray-400'}`}>
                    {item.rarity}
                  </td>
                  <td className="px-4 py-3 text-gray-400">{item.sell_price}</td>
                  <td className="px-4 py-3">
                    {item.is_tradable ? (
                      <span className="text-green-400 text-xs">Продается</span>
                    ) : (
                      <span className="text-gray-600 text-xs">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => openEdit(item)}
                        className="p-1.5 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors"
                        title="Редактировать"
                      >
                        <Pencil size={16} />
                      </button>
                      <button
                        onClick={() => setDeleteId(item.id)}
                        className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded transition-colors"
                        title="Удалить"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={closeForm} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 sticky top-0 bg-gray-800">
              <h3 className="text-lg font-bold">
                {editingItem ? 'Редактировать предмет' : 'Новый предмет'}
              </h3>
              <button onClick={closeForm} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Имя</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  placeholder="Название предмета"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Описание</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none resize-none"
                  rows={3}
                  placeholder="Описание предмета"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Тип</label>
                  <select
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value as ItemType })}
                    disabled={!!editingItem}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none disabled:opacity-50"
                  >
                    {ITEM_TYPES.map((t) => (
                      <option key={t} value={t}>{TYPE_LABELS[t]}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-1">Редкость</label>
                  <select
                    value={form.rarity}
                    onChange={(e) => setForm({ ...form, rarity: e.target.value as ItemRarity })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  >
                    {RARITIES.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
              </div>

              {effectFields.length > 0 && (
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Эффекты</label>
                  <div className="space-y-2">
                    {effectFields.map(({ key, label }) => (
                      <div key={key}>
                        <label className="block text-xs text-gray-500 mb-0.5">{label}</label>
                        <input
                          type="number"
                          step="any"
                          value={form[key] as string}
                          onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                          className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-white text-sm focus:border-blue-500 outline-none"
                          placeholder="0"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Цена продажи</label>
                  <input
                    type="number"
                    value={form.sell_price}
                    onChange={(e) => setForm({ ...form, sell_price: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>

                <div className="flex items-end pb-2">
                  <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.is_tradable}
                      onChange={(e) => setForm({ ...form, is_tradable: e.target.checked })}
                      className="w-4 h-4 accent-blue-600"
                    />
                    Можно продавать
                  </label>
                </div>
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-700 flex justify-end gap-3 sticky bottom-0 bg-gray-800">
              <button
                onClick={closeForm}
                className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors"
              >
                {submitting ? 'Сохранение...' : editingItem ? 'Сохранить' : 'Создать'}
              </button>
            </div>
          </div>
        </div>
      )}

      {deleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setDeleteId(null)} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-sm p-6">
            <h3 className="text-lg font-bold mb-2">Удалить предмет?</h3>
            <p className="text-sm text-gray-400 mb-6">Это действие нельзя отменить.</p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteId(null)}
                className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors"
              >
                {deleting ? 'Удаление...' : 'Удалить'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
