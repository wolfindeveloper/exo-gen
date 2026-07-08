import { useCallback, useEffect, useState } from 'react'
import { Dices, Pencil, Plus, Trash2, X } from 'lucide-react'

import { api } from '../../api/client'
import type { AdminLootBox, AdminItem, CreateLootBoxPayload, DropType, LootBoxSimResult, UpdateLootBoxPayload } from '../../types'

const DROP_TYPES: DropType[] = ['xgen', 'fragments', 'item']

const DROP_LABELS: Record<string, string> = {
  xgen: 'XGen',
  fragments: 'Фрагменты',
  item: 'Предмет',
}

interface LootRow {
  drop_type: DropType
  amount: string
  chance: string
  item_id: string
}

interface FormState {
  box_type: string
  name: string
  description: string
  is_active: boolean
  entries: LootRow[]
}

const EMPTY_FORM: FormState = {
  box_type: '',
  name: '',
  description: '',
  is_active: true,
  entries: [{ drop_type: 'xgen', amount: '50', chance: '1', item_id: '' }],
}

function formFromBox(box: AdminLootBox): FormState {
  return {
    box_type: box.box_type,
    name: box.name,
    description: box.description,
    is_active: box.is_active,
    entries: (box.entries || []).map((e) => ({
      drop_type: (e.item_type as DropType) || 'xgen',
      amount: String(e.amount),
      chance: String(e.chance),
      item_id: e.item_id || '',
    })),
  }
}

function buildEntries(rows: LootRow[]) {
  return rows.map((row) => ({
    item_type: row.drop_type,
    amount: parseInt(row.amount) || 1,
    chance: parseFloat(row.chance) || 0,
    item_id: row.drop_type === 'item' ? row.item_id : null,
  }))
}

export function LootBoxManager() {
  const [boxes, setBoxes] = useState<AdminLootBox[]>([])
  const [filtered, setFiltered] = useState<AdminLootBox[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [forbidden, setForbidden] = useState(false)
  const [search, setSearch] = useState('')

  const [showForm, setShowForm] = useState(false)
  const [editingBox, setEditingBox] = useState<AdminLootBox | null>(null)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)
  const [deletingBox, setDeletingBox] = useState<AdminLootBox | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')
  const [itemsList, setItemsList] = useState<AdminItem[]>([])

  const [simulating, setSimulating] = useState(false)
  const [simResults, setSimResults] = useState<{ box: AdminLootBox; results: LootBoxSimResult[] } | null>(null)

  const loadBoxes = useCallback(async () => {
    try {
      setLoading(true)
      setForbidden(false)
      setError(null)
      const data = await api.getAdminLootBoxes()
      setBoxes(data)
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
    loadBoxes()
  }, [loadBoxes])

  useEffect(() => {
    const q = search.toLowerCase()
    setFiltered(q ? boxes.filter((b) => b.name.toLowerCase().includes(q) || b.box_type.toLowerCase().includes(q)) : boxes)
  }, [search, boxes])

  const loadItemsList = useCallback(async () => {
    try {
      const data = await api.getAdminItems(1, 200)
      setItemsList(data.items)
    } catch { /* non-critical */ }
  }, [])

  const openCreate = () => {
    setEditingBox(null)
    setForm(EMPTY_FORM)
    setShowForm(true)
    loadItemsList()
  }

  const openEdit = (box: AdminLootBox) => {
    setEditingBox(box)
    setForm(formFromBox(box))
    setShowForm(true)
    loadItemsList()
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingBox(null)
    setForm(EMPTY_FORM)
  }

  const addEntry = () => {
    setForm({ ...form, entries: [...form.entries, { drop_type: 'xgen', amount: '1', chance: '0.5', item_id: '' }] })
  }

  const removeEntry = (index: number) => {
    setForm({ ...form, entries: form.entries.filter((_, i) => i !== index) })
  }

  const updateEntry = (index: number, field: keyof LootRow, value: string) => {
    const updated = [...form.entries]
    updated[index] = { ...updated[index], [field]: value }
    if (field === 'drop_type' && value !== 'item') {
      updated[index].item_id = ''
    }
    setForm({ ...form, entries: updated })
  }

  const handleSubmit = async () => {
    if (!form.box_type.trim() || !form.name.trim() || !form.description.trim()) {
      setError('Тип, имя и описание обязательны')
      return
    }
    const invalidItem = form.entries.find((row) => row.drop_type === 'item' && !row.item_id)
    if (invalidItem) {
      setError('Для каждого дропа типа "Предмет" нужно выбрать предмет')
      return
    }
    try {
      setSubmitting(true)
      setError(null)
      const entries = buildEntries(form.entries)
      if (editingBox) {
        const payload: UpdateLootBoxPayload = {
          name: form.name,
          description: form.description,
          entries,
          is_active: form.is_active,
        }
        await api.updateAdminLootBox(editingBox.id, payload)
      } else {
        const payload: CreateLootBoxPayload = {
          box_type: form.box_type,
          name: form.name,
          description: form.description,
          entries,
          is_active: form.is_active,
        }
        await api.createAdminLootBox(payload)
      }
      closeForm()
      await loadBoxes()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const confirmDelete = async () => {
    if (!deletingBox) return
    try {
      setDeleting(true)
      setDeleteError('')
      await api.deleteAdminLootBox(deletingBox.id)
      setDeletingBox(null)
      await loadBoxes()
    } catch (e) {
      setDeleteError((e as Error).message)
    } finally {
      setDeleting(false)
    }
  }

  const handleSimulate = async (box: AdminLootBox) => {
    try {
      setSimulating(true)
      setError(null)
      const results = await api.simulateLootBox(box.id, 1000)
      setSimResults({ box, results })
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSimulating(false)
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

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-xl font-bold">Лутбоксы</h2>
          <p className="text-sm text-gray-500">Всего: {boxes.length}</p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
        >
          <Plus size={18} />
          Создать лутбокс
        </button>
      </div>

      <div className="mb-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Поиск по имени или типу..."
          className="w-full sm:max-w-xs bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
        />
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
      ) : filtered.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-500">
          {search ? 'Ничего не найдено' : 'Лутбоксов пока нет. Создайте первый!'}
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg overflow-x-auto mb-4">
          <table className="w-full text-sm min-w-[520px]">
            <thead>
              <tr className="bg-gray-750 border-b border-gray-700 text-left text-gray-400">
                <th className="px-3 py-3 font-medium">Тип</th>
                <th className="px-3 py-3 font-medium">Имя</th>
                <th className="px-3 py-3 font-medium hidden sm:table-cell">Дропы</th>
                <th className="px-3 py-3 font-medium hidden sm:table-cell">Статус</th>
                <th className="px-3 py-3 font-medium text-right">Действия</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((box) => (
                <tr key={box.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                  <td className="px-3 py-3 font-mono text-xs text-blue-400">{box.box_type}</td>
                  <td className="px-3 py-3 font-medium text-white">{box.name}</td>
                  <td className="px-3 py-3 text-gray-400 hidden sm:table-cell">{box.entries?.length || 0}</td>
                  <td className="px-3 py-3 hidden sm:table-cell">
                    {box.is_active ? (
                      <span className="text-green-400 text-xs">Активен</span>
                    ) : (
                      <span className="text-gray-600 text-xs">Выключен</span>
                    )}
                  </td>
                  <td className="px-3 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleSimulate(box)}
                        disabled={simulating}
                        className="flex items-center gap-1 text-xs bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 px-2 py-1 rounded transition-colors disabled:opacity-30"
                        title="Симуляция x1000"
                      >
                        <Dices size={14} />
                        x1000
                      </button>
                      <button
                        onClick={() => openEdit(box)}
                        className="p-1.5 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors"
                        title="Редактировать"
                      >
                        <Pencil size={16} />
                      </button>
                      <button
                        onClick={() => setDeletingBox(box)}
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
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-lg max-h-[90vh] overflow-y-auto mx-4">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 sticky top-0 bg-gray-800 z-10">
              <h3 className="text-lg font-bold">
                {editingBox ? 'Редактировать лутбокс' : 'Новый лутбокс'}
              </h3>
              <button onClick={closeForm} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Тип бокса (box_type)</label>
                <input
                  type="text"
                  value={form.box_type}
                  onChange={(e) => setForm({ ...form, box_type: e.target.value })}
                  disabled={!!editingBox}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none disabled:opacity-50 font-mono text-sm"
                  placeholder="WELCOME, DAILY_42, SHOP или свой кастомный"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Имя</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  placeholder="Название лутбокса"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Описание</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none resize-none"
                  rows={2}
                  placeholder="Описание лутбокса"
                />
              </div>

              <div>
                <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.is_active}
                    onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                    className="w-4 h-4 accent-blue-600"
                  />
                  Активен
                </label>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm text-gray-400">Содержимое (entries)</label>
                  <button
                    type="button"
                    onClick={addEntry}
                    className="flex items-center gap-1 text-xs bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 px-2 py-1 rounded transition-colors"
                  >
                    <Plus size={14} />
                    Добавить дроп
                  </button>
                </div>
                <div className="space-y-2">
                  {form.entries.map((row, i) => (
                    <div key={i} className="flex flex-wrap items-center gap-2 bg-gray-900/50 border border-gray-700 rounded-lg p-2">
                      <select
                        value={row.drop_type}
                        onChange={(e) => updateEntry(i, 'drop_type', e.target.value)}
                        className="bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:border-blue-500 outline-none"
                      >
                        {DROP_TYPES.map((t) => (
                          <option key={t} value={t}>{DROP_LABELS[t]}</option>
                        ))}
                      </select>
                      <input
                        type="number"
                        value={row.amount}
                        onChange={(e) => updateEntry(i, 'amount', e.target.value)}
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
                        onChange={(e) => updateEntry(i, 'chance', e.target.value)}
                        className="w-16 bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:border-blue-500 outline-none"
                        placeholder="Шанс"
                      />
                      {row.drop_type === 'item' && (
                        <select
                          value={row.item_id}
                          onChange={(e) => updateEntry(i, 'item_id', e.target.value)}
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
                        onClick={() => removeEntry(i)}
                        className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
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
                {submitting ? 'Сохранение...' : editingBox ? 'Сохранить' : 'Создать'}
              </button>
            </div>
          </div>
        </div>
      )}

      {deletingBox && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setDeletingBox(null)} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-sm p-6">
            <h3 className="text-lg font-bold mb-2">Удалить лутбокс?</h3>
            <p className="text-sm text-gray-400 mb-6">
              Вы уверены, что хотите удалить лутбокс «{deletingBox.name}» ({deletingBox.box_type})? Это мягкое удаление.
            </p>
            {deleteError && <div className="mb-4 bg-red-900/30 border border-red-700/50 text-red-300 px-3 py-2 rounded-lg text-sm">{deleteError}</div>}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeletingBox(null)}
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
                <h3 className="text-lg font-bold">Симуляция x1000</h3>
                <p className="text-xs text-gray-500">{simResults.box.name} ({simResults.box.box_type})</p>
              </div>
              <button onClick={() => setSimResults(null)} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6">
              {simResults.results.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Нет данных. Возможно, entries пусты.</p>
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
