import { useCallback, useEffect, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight, Dices, Pencil, Plus, Search, Trash2, X } from 'lucide-react'

import { api } from '../../api/client'
import type { AdminZone, AdminZonesResponse, AdminItem, CreateZonePayload, DropType, LootBoxSimResult, UpdateZonePayload } from '../../types'

const DROP_TYPES: DropType[] = ['xgen', 'fragments', 'item']

const DROP_LABELS: Record<string, string> = {
  xgen: 'XGen',
  fragments: 'Фрагменты',
  item: 'Предмет',
}

const SORT_OPTIONS: { value: string; label: string }[] = [
  { value: 'name', label: 'По имени' },
  { value: 'fuel_cost', label: 'По топливу' },
  { value: 'duration_seconds', label: 'По длительности' },
]

const PAGE_SIZE = 20

interface LootRow {
  drop_type: DropType
  amount: string
  chance: string
  item_id: string
}

interface FormState {
  name: string
  description: string
  image_url: string
  fuel_cost: string
  optimism_risk: string
  duration_seconds: string
  loot_table: LootRow[]
}

const EMPTY_FORM: FormState = {
  name: '',
  description: '',
  image_url: '',
  fuel_cost: '10',
  optimism_risk: '5',
  duration_seconds: '3600',
  loot_table: [{ drop_type: 'xgen', amount: '50', chance: '1', item_id: '' }],
}

function formFromZone(zone: AdminZone): FormState {
  return {
    name: zone.name,
    description: zone.description,
    image_url: zone.image_url || '',
    fuel_cost: String(zone.fuel_cost),
    optimism_risk: String(zone.optimism_risk),
    duration_seconds: String(zone.duration_seconds),
    loot_table: (zone.loot_table || []).map((entry) => ({
      drop_type: entry.drop_type,
      amount: String(entry.amount),
      chance: String(entry.chance),
      item_id: entry.item_id || '',
    })),
  }
}

function buildLootTable(rows: LootRow[]): { drop_type: DropType; amount: number; chance: number; item_id?: string | null }[] {
  return rows.map((row) => ({
    drop_type: row.drop_type,
    amount: parseInt(row.amount) || 1,
    chance: parseFloat(row.chance) || 0,
    item_id: row.drop_type === 'item' ? row.item_id : null,
  }))
}

function formatDuration(seconds: number): string {
  if (seconds >= 3600) {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    return m > 0 ? `${h}ч ${m}м` : `${h}ч`
  }
  if (seconds >= 60) return `${Math.floor(seconds / 60)}м`
  return `${seconds}с`
}

export function ZonesManager() {
  const [zones, setZones] = useState<AdminZone[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [forbidden, setForbidden] = useState(false)

  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [sortBy, setSortBy] = useState<string | undefined>(undefined)
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const [showForm, setShowForm] = useState(false)
  const [editingZone, setEditingZone] = useState<AdminZone | null>(null)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)
  const [deletingZone, setDeletingZone] = useState<AdminZone | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')
  const [itemsList, setItemsList] = useState<AdminItem[]>([])

  const [simulating, setSimulating] = useState(false)
  const [simResults, setSimResults] = useState<{ zone: AdminZone; results: LootBoxSimResult[] } | null>(null)

  const searchTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const loadZones = useCallback(async (p: number, s: string, sb?: string, so?: 'asc' | 'desc') => {
    try {
      setLoading(true)
      setForbidden(false)
      setError(null)
      const data: AdminZonesResponse = await api.getAdminZones(p, PAGE_SIZE, s || undefined, sb, so)
      setZones(data.items)
      setTotal(data.total)
      setTotalPages(data.total_pages)
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
    loadZones(page, search, sortBy, sortOrder)
  }, [page, search, sortBy, sortOrder, loadZones])

  const loadItemsList = useCallback(async () => {
    try {
      const data = await api.getAdminItems(1, 200)
      setItemsList(data.items)
    } catch {
      // non-critical
    }
  }, [])

  const handleSearchInput = (val: string) => {
    setSearchInput(val)
    if (searchTimer.current) clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => {
      setPage(1)
      setSearch(val)
    }, 400)
  }

  const handleSort = (col: string) => {
    if (sortBy === col) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(col)
      setSortOrder('asc')
    }
    setPage(1)
  }

  const handleSimulate = async (zone: AdminZone) => {
    try {
      setSimulating(true)
      setError(null)
      const results = await api.simulateZone(zone.id, 100)
      const totalXgen = results.reduce((sum, r) => r.drop_type === 'xgen' ? sum + r.total_dropped : sum, 0)
      const totalFragments = results.reduce((sum, r) => r.drop_type === 'fragments' ? sum + r.total_dropped : sum, 0)
      const enriched: LootBoxSimResult[] = results.map((r) => ({
        ...r,
        total_xgen: r.drop_type === 'xgen' ? totalXgen : null,
        total_fragments: r.drop_type === 'fragments' ? totalFragments : null,
      }))
      setSimResults({ zone, results: enriched })
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSimulating(false)
    }
  }

  const openCreate = () => {
    setEditingZone(null)
    setForm(EMPTY_FORM)
    setShowForm(true)
    loadItemsList()
  }

  const openEdit = (zone: AdminZone) => {
    setEditingZone(zone)
    setForm(formFromZone(zone))
    setShowForm(true)
    loadItemsList()
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingZone(null)
    setForm(EMPTY_FORM)
  }

  const addLootRow = () => {
    setForm({ ...form, loot_table: [...form.loot_table, { drop_type: 'xgen', amount: '1', chance: '0.5', item_id: '' }] })
  }

  const removeLootRow = (index: number) => {
    setForm({ ...form, loot_table: form.loot_table.filter((_, i) => i !== index) })
  }

  const updateLootRow = (index: number, field: keyof LootRow, value: string) => {
    const updated = [...form.loot_table]
    updated[index] = { ...updated[index], [field]: value }
    if (field === 'drop_type' && value !== 'item') {
      updated[index].item_id = ''
    }
    setForm({ ...form, loot_table: updated })
  }

  const handleSubmit = async () => {
    if (!form.name.trim() || !form.description.trim()) {
      setError('Имя и описание обязательны')
      return
    }
    if (!form.image_url.trim()) {
      setError('URL картинки обязателен')
      return
    }
    if (form.loot_table.length === 0) {
      setError('Лут-таблица не может быть пустой')
      return
    }
    const invalidItem = form.loot_table.find((row) => row.drop_type === 'item' && !row.item_id)
    if (invalidItem) {
      setError('Для каждого дропа типа "Предмет" нужно выбрать предмет')
      return
    }
    try {
      setSubmitting(true)
      setError(null)
      const loot_table = buildLootTable(form.loot_table)
      if (editingZone) {
        const payload: UpdateZonePayload = {
          name: form.name,
          description: form.description,
          image_url: form.image_url,
          fuel_cost: parseFloat(form.fuel_cost) || 0,
          optimism_risk: parseFloat(form.optimism_risk) || 0,
          duration_seconds: parseInt(form.duration_seconds) || 0,
          loot_table,
        }
        await api.updateAdminZone(editingZone.id, payload)
      } else {
        const payload: CreateZonePayload = {
          name: form.name,
          description: form.description,
          image_url: form.image_url,
          fuel_cost: parseFloat(form.fuel_cost) || 0,
          optimism_risk: parseFloat(form.optimism_risk) || 0,
          duration_seconds: parseInt(form.duration_seconds) || 0,
          loot_table,
        }
        await api.createAdminZone(payload)
      }
      closeForm()
      await loadZones(page, search, sortBy, sortOrder)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const confirmDelete = async () => {
    if (!deletingZone) return
    try {
      setDeleting(true)
      setDeleteError('')
      await api.deleteAdminZone(deletingZone.id)
      setDeletingZone(null)
      await loadZones(page, search, sortBy, sortOrder)
    } catch (e) {
      setDeleteError((e as Error).message)
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

  const sortIcon = (col: string) => {
    if (sortBy !== col) return null
    return sortOrder === 'asc' ? ' ↑' : ' ↓'
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-xl font-bold">Зоны</h2>
          <p className="text-sm text-gray-500">Всего: {total}</p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
        >
          <Plus size={18} />
          Создать зону
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-2 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => handleSearchInput(e.target.value)}
            placeholder="Поиск по имени..."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
          />
        </div>
        <select
          value={sortBy || ''}
          onChange={(e) => { setSortBy(e.target.value || undefined); setPage(1) }}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
        >
          <option value="">Без сортировки</option>
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="mb-4 bg-red-900/30 border border-red-700/50 text-red-300 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <p className="text-gray-400 animate-pulse">Загрузка...</p>
        </div>
      ) : zones.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-500">
          {search ? 'Ничего не найдено' : 'Зон пока нет. Создайте первую!'}
        </div>
      ) : (
        <>
          <div className="bg-gray-800 rounded-lg overflow-x-auto mb-4">
            <table className="w-full text-sm min-w-[520px]">
              <thead>
                <tr className="bg-gray-750 border-b border-gray-700 text-left text-gray-400">
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('name')}>
                    Имя{sortIcon('name')}
                  </th>
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('fuel_cost')}>
                    ⛽{sortIcon('fuel_cost')}
                  </th>
                  <th className="px-3 py-3 font-medium">⚠ Риск</th>
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('duration_seconds')}>
                    ⏱ Время{sortIcon('duration_seconds')}
                  </th>
                  <th className="px-3 py-3 font-medium hidden sm:table-cell">Дропы</th>
                  <th className="px-3 py-3 font-medium text-right">Действия</th>
                </tr>
              </thead>
              <tbody>
                {zones.map((zone) => (
                  <tr key={zone.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                    <td className="px-3 py-3 font-medium text-white">
                      <div className="flex items-center gap-2">
                        {zone.image_url && (
                          <img src={zone.image_url} alt="" className="w-7 h-7 rounded object-cover shrink-0" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }} />
                        )}
                        {zone.name}
                      </div>
                    </td>
                    <td className="px-3 py-3 text-gray-400">{zone.fuel_cost}</td>
                    <td className="px-3 py-3 text-gray-400">{zone.optimism_risk}%</td>
                    <td className="px-3 py-3 text-gray-400">{formatDuration(zone.duration_seconds)}</td>
                    <td className="px-3 py-3 text-gray-400 hidden sm:table-cell">{zone.loot_table?.length || 0}</td>
                    <td className="px-3 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleSimulate(zone)}
                          disabled={simulating}
                          className="flex items-center gap-1 text-xs bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 px-2 py-1 rounded transition-colors disabled:opacity-30"
                          title="Симуляция x100"
                        >
                          <Dices size={14} />
                          x100
                        </button>
                        <button
                          onClick={() => openEdit(zone)}
                          className="p-1.5 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors"
                          title="Редактировать"
                        >
                          <Pencil size={16} />
                        </button>
                        <button
                          onClick={() => { setDeletingZone(zone); setDeleteError('') }}
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

          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-xs text-gray-500">Стр. {page} из {totalPages}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page <= 1}
                  className="flex items-center gap-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 text-gray-300 px-3 py-1.5 rounded-lg text-sm transition-colors"
                >
                  <ChevronLeft size={16} />
                  Назад
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page >= totalPages}
                  className="flex items-center gap-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 text-gray-300 px-3 py-1.5 rounded-lg text-sm transition-colors"
                >
                  Вперёд
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={closeForm} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-lg max-h-[90vh] overflow-y-auto mx-4">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 sticky top-0 bg-gray-800 z-10">
              <h3 className="text-lg font-bold">
                {editingZone ? 'Редактировать зону' : 'Новая зона'}
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
                  placeholder="Название зоны"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Описание</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none resize-none"
                  rows={3}
                  placeholder="Описание зоны"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Картинка (URL)</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={form.image_url}
                    onChange={(e) => setForm({ ...form, image_url: e.target.value })}
                    className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                    placeholder="/assets/zones/..."
                  />
                  {form.image_url && (
                    <img src={form.image_url} alt="" className="w-10 h-10 rounded-lg object-cover border border-gray-700" onError={(e) => { (e.target as HTMLImageElement).style.opacity = '0.3' }} />
                  )}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">⛽ Топливо</label>
                  <input
                    type="number"
                    step="any"
                    value={form.fuel_cost}
                    onChange={(e) => setForm({ ...form, fuel_cost: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">⚠ Риск (%)</label>
                  <input
                    type="number"
                    step="any"
                    min="0"
                    max="100"
                    value={form.optimism_risk}
                    onChange={(e) => setForm({ ...form, optimism_risk: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">⏱ Секунд</label>
                  <input
                    type="number"
                    value={form.duration_seconds}
                    onChange={(e) => setForm({ ...form, duration_seconds: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm text-gray-400">Дропы (лут-таблица)</label>
                  <button
                    type="button"
                    onClick={addLootRow}
                    className="flex items-center gap-1 text-xs bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 px-2 py-1 rounded transition-colors"
                  >
                    <Plus size={14} />
                    Добавить дроп
                  </button>
                </div>
                <div className="space-y-2">
                  {form.loot_table.map((row, i) => (
                    <div key={i} className="flex flex-wrap items-center gap-2 bg-gray-900/50 border border-gray-700 rounded-lg p-2">
                      <select
                        value={row.drop_type}
                        onChange={(e) => updateLootRow(i, 'drop_type', e.target.value)}
                        className="bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:border-blue-500 outline-none"
                      >
                        {DROP_TYPES.map((t) => (
                          <option key={t} value={t}>{DROP_LABELS[t]}</option>
                        ))}
                      </select>
                      <input
                        type="number"
                        value={row.amount}
                        onChange={(e) => updateLootRow(i, 'amount', e.target.value)}
                        className="w-16 bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:border-blue-500 outline-none"
                        placeholder="Кол-во"
                        min="1"
                      />
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        max="1"
                        value={row.chance}
                        onChange={(e) => updateLootRow(i, 'chance', e.target.value)}
                        className="w-16 bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:border-blue-500 outline-none"
                        placeholder="Шанс"
                      />
                      {row.drop_type === 'item' && (
                        <select
                          value={row.item_id}
                          onChange={(e) => updateLootRow(i, 'item_id', e.target.value)}
                          className={`flex-1 min-w-[120px] bg-gray-900 border rounded px-2 py-1.5 text-white text-xs outline-none ${
                            !row.item_id ? 'border-red-500' : 'border-gray-700 focus:border-blue-500'
                          }`}
                        >
                          <option value="">— выберите предмет —</option>
                          {itemsList.map((item) => (
                            <option key={item.id} value={item.id}>{item.name}</option>
                          ))}
                        </select>
                      )}
                      <button
                        type="button"
                        onClick={() => removeLootRow(i)}
                        className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                  {form.loot_table.length === 0 && (
                    <p className="text-xs text-gray-600 italic">Добавьте хотя бы один дроп</p>
                  )}
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
                {submitting ? 'Сохранение...' : editingZone ? 'Сохранить' : 'Создать'}
              </button>
            </div>
          </div>
        </div>
      )}

      {deletingZone && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setDeletingZone(null)} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-sm p-6">
            <h3 className="text-lg font-bold mb-2">Удалить зону?</h3>
            <p className="text-sm text-gray-400 mb-6">
              Вы уверены, что хотите удалить зону «{deletingZone.name}»? Это мягкое удаление, зона пометится как удаленная.
            </p>
            {deleteError && <div className="mb-4 bg-red-900/30 border border-red-700/50 text-red-300 px-3 py-2 rounded-lg text-sm">{deleteError}</div>}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeletingZone(null)}
                className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={confirmDelete}
                disabled={deleting}
                className="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors"
              >
                {deleting ? 'Удаление...' : 'Удалить'}
              </button>
            </div>
          </div>
        </div>
      )}

      {simResults && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSimResults(null)} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-lg max-h-[80vh] overflow-y-auto mx-4">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 sticky top-0 bg-gray-800 z-10">
              <div>
                <h3 className="text-lg font-bold">Предпросмотр лута зоны: {simResults.zone.name}</h3>
                <p className="text-xs text-gray-500">Симуляция x100 экспедиций</p>
              </div>
              <button onClick={() => setSimResults(null)} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6">
              {simResults.results.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Нет данных. Возможно, loot_table пуста.</p>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700 text-left text-gray-400">
                      <th className="py-2 font-medium">Дроп</th>
                      <th className="py-2 font-medium text-right">Кол-во</th>
                      <th className="py-2 font-medium text-right">Процент</th>
                    </tr>
                  </thead>
                  <tbody>
                    {simResults.results.map((r, i) => (
                      <tr key={i} className="border-b border-gray-700/50">
                        <td className="py-2 text-white">
                          {r.drop_type === 'item' ? (r.item_name || r.item_id || 'Предмет') : DROP_LABELS[r.drop_type] || r.drop_type}
                        </td>
                        <td className="py-2 text-right text-gray-300 font-mono">{r.total_dropped}</td>
                        <td className="py-2 text-right text-purple-400 font-mono">{r.percentage}%</td>
                      </tr>
                    ))}
                  </tbody>
                  {simResults.results[0]?.total_xgen != null && (
                    <tfoot>
                      <tr className="border-t-2 border-gray-700">
                        <td className="py-3 font-medium text-gray-400">Всего XGen</td>
                        <td className="py-3 text-right text-green-400 font-mono" colSpan={2}>{simResults.results[0].total_xgen}</td>
                      </tr>
                      {simResults.results[0]?.total_fragments != null && (
                        <tr>
                          <td className="py-2 font-medium text-gray-400">Всего фрагментов</td>
                          <td className="py-2 text-right text-amber-400 font-mono" colSpan={2}>{simResults.results[0].total_fragments}</td>
                        </tr>
                      )}
                    </tfoot>
                  )}
                </table>
              )}
            </div>

            <div className="px-6 py-4 border-t border-gray-700 flex justify-end">
              <button
                onClick={() => setSimResults(null)}
                className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors"
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
