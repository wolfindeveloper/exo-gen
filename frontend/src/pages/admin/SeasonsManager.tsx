import { useCallback, useEffect, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight, Pencil, Plus, Search, Trash2, X } from 'lucide-react'

import { api } from '../../api/client'
import type { AdminSeason } from '../../types'

const PAGE_SIZE = 20

const SORT_OPTIONS: { value: string; label: string }[] = [
  { value: 'name', label: 'По имени' },
  { value: 'start_date', label: 'По дате начала' },
  { value: 'end_date', label: 'По дате окончания' },
]

function toDatetimeLocal(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return ''
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function toUTCISO(local: string): string {
  if (!local) return ''
  const d = new Date(local)
  return isNaN(d.getTime()) ? '' : d.toISOString()
}

interface FormState {
  name: string
  description: string
  start_date: string
  end_date: string
  reward_xgen: string
  reward_fragments: string
  is_active: boolean
}

const EMPTY_FORM: FormState = {
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  reward_xgen: '0',
  reward_fragments: '0',
  is_active: true,
}

type DeleteModalType = 'error_active' | 'warning_future' | 'confirm' | null

export function SeasonsManager() {
  const [seasons, setSeasons] = useState<AdminSeason[]>([])
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
  const [editingItem, setEditingItem] = useState<AdminSeason | null>(null)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)

  const [deletingItem, setDeletingItem] = useState<AdminSeason | null>(null)
  const [deleteModalType, setDeleteModalType] = useState<DeleteModalType>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  const searchTimer = useRef<ReturnType<typeof setTimeout>>(undefined)

  const loadItems = useCallback(async (p: number, s: string, sb?: string, so?: 'asc' | 'desc') => {
    try {
      setLoading(true)
      setForbidden(false)
      setError(null)
      const data = await api.getAdminSeasons(p, PAGE_SIZE, s || undefined, sb, so)
      setSeasons(data.items)
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
    loadItems(page, search, sortBy, sortOrder)
  }, [page, search, sortBy, sortOrder, loadItems])

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

  const sortIcon = (col: string) => {
    if (sortBy !== col) return null
    return sortOrder === 'asc' ? ' \u2191' : ' \u2193'
  }

  const formatDate = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const openCreate = () => {
    setEditingItem(null)
    setForm(EMPTY_FORM)
    setShowForm(true)
  }

  const openEdit = (item: AdminSeason) => {
    setEditingItem(item)
    setForm({
      name: item.name,
      description: item.description,
      start_date: toDatetimeLocal(item.start_date),
      end_date: toDatetimeLocal(item.end_date),
      reward_xgen: String(item.reward_xgen),
      reward_fragments: String(item.reward_fragments),
      is_active: item.is_active,
    })
    setShowForm(true)
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingItem(null)
    setForm(EMPTY_FORM)
  }

  const handleSubmit = async () => {
    if (!form.name.trim() || !form.description.trim()) {
      setError('\u0418\u043c\u044f \u0438 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u044b')
      return
    }
    if (!form.start_date || !form.end_date) {
      setError('\u0414\u0430\u0442\u044b \u043d\u0430\u0447\u0430\u043b\u0430 \u0438 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u044b')
      return
    }
    if (new Date(form.end_date) <= new Date(form.start_date)) {
      setError('\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0434\u043e\u043b\u0436\u043d\u0430 \u0431\u044b\u0442\u044c \u043f\u043e\u0437\u0436\u0435 \u0434\u0430\u0442\u044b \u043d\u0430\u0447\u0430\u043b\u0430')
      return
    }

    try {
      setSubmitting(true)
      setError(null)

      const payload = {
        name: form.name,
        description: form.description,
        start_date: toUTCISO(form.start_date),
        end_date: toUTCISO(form.end_date),
        reward_xgen: parseInt(form.reward_xgen) || 0,
        reward_fragments: parseInt(form.reward_fragments) || 0,
        is_active: form.is_active,
      }

      if (editingItem) {
        await api.updateAdminSeason(editingItem.id, payload)
      } else {
        await api.createAdminSeason(payload)
      }

      closeForm()
      await loadItems(page, search, sortBy, sortOrder)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = (item: AdminSeason) => {
    setDeletingItem(item)
    setDeleteError('')

    if (item.is_active) {
      setDeleteModalType('error_active')
    } else if (new Date(item.end_date) > new Date()) {
      setDeleteModalType('warning_future')
    } else {
      setDeleteModalType('confirm')
    }
  }

  const confirmDelete = async () => {
    if (!deletingItem) return
    try {
      setDeleting(true)
      setDeleteError('')
      await api.deleteAdminSeason(deletingItem.id)
      setDeletingItem(null)
      setDeleteModalType(null)
      await loadItems(page, search, sortBy, sortOrder)
    } catch (e) {
      setDeleteError((e as Error).message)
    } finally {
      setDeleting(false)
    }
  }

  const closeDeleteModal = () => {
    setDeletingItem(null)
    setDeleteModalType(null)
  }

  if (forbidden) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-2xl mb-2">{'\uD83D\uDD12'}</p>
          <p className="text-red-400 text-lg font-medium">{'\u0414\u043e\u0441\u0442\u0443\u043f \u0437\u0430\u043f\u0440\u0435\u0449\u0435\u043d. \u0412\u044b \u043d\u0435 \u044f\u0432\u043b\u044f\u0435\u0442\u0435\u0441\u044c \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440\u043e\u043c.'}</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-xl font-bold">{'\u0421\u0435\u0437\u043e\u043d\u044b'}</h2>
          <p className="text-sm text-gray-500">{'\u0412\u0441\u0435\u0433\u043e:'} {total}</p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
        >
          <Plus size={18} />
          {'\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0441\u0435\u0437\u043e\u043d'}
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-2 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => handleSearchInput(e.target.value)}
            placeholder={'\u041f\u043e\u0438\u0441\u043a \u043f\u043e \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u044e...'}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
          />
        </div>
        <select
          value={sortBy || ''}
          onChange={(e) => { setSortBy(e.target.value || undefined); setPage(1) }}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
        >
          <option value="">{'\u0411\u0435\u0437 \u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0438'}</option>
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
          <p className="text-gray-400 animate-pulse">{'\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430...'}</p>
        </div>
      ) : seasons.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-500">
          {search ? '\u041d\u0438\u0447\u0435\u0433\u043e \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e' : '\u0421\u0435\u0437\u043e\u043d\u043e\u0432 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442. \u0421\u043e\u0437\u0434\u0430\u0439\u0442\u0435 \u043f\u0435\u0440\u0432\u044b\u0439!'}
        </div>
      ) : (
        <>
          <div className="bg-gray-800 rounded-lg overflow-x-auto mb-4">
            <table className="w-full text-sm min-w-[640px]">
              <thead>
                <tr className="bg-gray-750 border-b border-gray-700 text-left text-gray-400">
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('name')}>
                    {'\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435'}{sortIcon('name')}
                  </th>
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('start_date')}>
                    {'\u041d\u0430\u0447\u0430\u043b\u043e'}{sortIcon('start_date')}
                  </th>
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('end_date')}>
                    {'\u041e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u0435'}{sortIcon('end_date')}
                  </th>
                  <th className="px-3 py-3 font-medium hidden sm:table-cell">{'\u041d\u0430\u0433\u0440\u0430\u0434\u044b'}</th>
                  <th className="px-3 py-3 font-medium hidden sm:table-cell">{'\u0421\u0442\u0430\u0442\u0443\u0441'}</th>
                  <th className="px-3 py-3 font-medium text-right">{'\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u044f'}</th>
                </tr>
              </thead>
              <tbody>
                {seasons.map((item) => (
                  <tr key={item.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                    <td className="px-3 py-3 font-medium text-white">{item.name}</td>
                    <td className="px-3 py-3 text-gray-400 text-xs">{formatDate(item.start_date)}</td>
                    <td className="px-3 py-3 text-gray-400 text-xs">{formatDate(item.end_date)}</td>
                    <td className="px-3 py-3 text-gray-400 text-xs hidden sm:table-cell">
                      {item.reward_xgen > 0 && <span className="text-cyan-400">{item.reward_xgen} XGen </span>}
                      {item.reward_fragments > 0 && <span className="text-purple-400">{item.reward_fragments} Frags</span>}
                      {item.reward_xgen === 0 && item.reward_fragments === 0 && '\u2014'}
                    </td>
                    <td className="px-3 py-3 hidden sm:table-cell">
                      {item.is_active ? (
                        <span className="text-green-400 text-xs">{'\u0410\u043a\u0442\u0438\u0432\u0435\u043d'}</span>
                      ) : (
                        <span className="text-red-400 text-xs">{'\u041d\u0435\u0430\u043a\u0442\u0438\u0432\u0435\u043d'}</span>
                      )}
                    </td>
                    <td className="px-3 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openEdit(item)}
                          className="p-1.5 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors"
                          title={'\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c'}
                        >
                          <Pencil size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(item)}
                          className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded transition-colors"
                          title={'\u0423\u0434\u0430\u043b\u0438\u0442\u044c'}
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
              <p className="text-xs text-gray-500">{'\u0421\u0442\u0440.'} {page} {'\u0438\u0437'} {totalPages}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page <= 1}
                  className="flex items-center gap-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 text-gray-300 px-3 py-1.5 rounded-lg text-sm transition-colors"
                >
                  <ChevronLeft size={16} />
                  {'\u041d\u0430\u0437\u0430\u0434'}
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page >= totalPages}
                  className="flex items-center gap-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-30 text-gray-300 px-3 py-1.5 rounded-lg text-sm transition-colors"
                >
                  {'\u0412\u043f\u0435\u0440\u0451\u0434'}
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
                {editingItem ? '\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0441\u0435\u0437\u043e\u043d' : '\u041d\u043e\u0432\u044b\u0439 \u0441\u0435\u0437\u043e\u043d'}
              </h3>
              <button onClick={closeForm} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">{'\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435'}</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  placeholder={'\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0441\u0435\u0437\u043e\u043d\u0430'}
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">{'\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435'}</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none resize-none"
                  rows={3}
                  placeholder={'\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0441\u0435\u0437\u043e\u043d\u0430'}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{'\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430'}</label>
                  <input
                    type="datetime-local"
                    value={form.start_date}
                    onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{'\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f'}</label>
                  <input
                    type="datetime-local"
                    value={form.end_date}
                    onChange={(e) => setForm({ ...form, end_date: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{'reward_xgen'}</label>
                  <input
                    type="number"
                    min={0}
                    value={form.reward_xgen}
                    onChange={(e) => setForm({ ...form, reward_xgen: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{'reward_fragments'}</label>
                  <input
                    type="number"
                    min={0}
                    value={form.reward_fragments}
                    onChange={(e) => setForm({ ...form, reward_fragments: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
              </div>

              <div className="flex items-center">
                <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.is_active}
                    onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                    className="w-4 h-4 accent-blue-600"
                  />
                  {'\u0410\u043a\u0442\u0438\u0432\u0435\u043d'}
                </label>
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-700 flex justify-end gap-3 sticky bottom-0 bg-gray-800">
              <button
                onClick={closeForm}
                className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
              >
                {'\u041e\u0442\u043c\u0435\u043d\u0430'}
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors"
              >
                {submitting ? '\u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u0435...' : editingItem ? '\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c' : '\u0421\u043e\u0437\u0434\u0430\u0442\u044c'}
              </button>
            </div>
          </div>
        </div>
      )}

      {deletingItem && deleteModalType && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={closeDeleteModal} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-sm p-6">
            {deleteError && <div className="mb-4 bg-red-900/30 border border-red-700/50 text-red-300 px-3 py-2 rounded-lg text-sm">{deleteError}</div>}
            {deleteModalType === 'error_active' && (
              <>
                <h3 className="text-lg font-bold mb-2 text-red-400">{'\u041e\u0448\u0438\u0431\u043a\u0430'}</h3>
                <p className="text-sm text-gray-400 mb-6">
                  {'\u041d\u0435\u043b\u044c\u0437\u044f \u0443\u0434\u0430\u043b\u0438\u0442\u044c \u0430\u043a\u0442\u0438\u0432\u043d\u044b\u0439 \u0441\u0435\u0437\u043e\u043d. \u0421\u043d\u0430\u0447\u0430\u043b\u0430 \u0434\u0435\u0430\u043a\u0442\u0438\u0432\u0438\u0440\u0443\u0439\u0442\u0435 \u0435\u0433\u043e.'}
                </p>
                <div className="flex justify-end">
                  <button
                    onClick={closeDeleteModal}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm transition-colors"
                  >
                    OK
                  </button>
                </div>
              </>
            )}

            {deleteModalType === 'warning_future' && (
              <>
                <h3 className="text-lg font-bold mb-2 text-amber-400">{'\u0412\u043d\u0438\u043c\u0430\u043d\u0438\u0435'}</h3>
                <p className="text-sm text-gray-400 mb-6">
                  {'\u0421\u0435\u0437\u043e\u043d \u0435\u0449\u0435 \u043d\u0435 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d \u043f\u043e \u0432\u0440\u0435\u043c\u0435\u043d\u0438. \u0412\u044b \u0443\u0432\u0435\u0440\u0435\u043d\u044b, \u0447\u0442\u043e \u0445\u043e\u0442\u0438\u0442\u0435 \u0435\u0433\u043e \u0443\u0434\u0430\u043b\u0438\u0442\u044c?'}
                </p>
                <div className="flex justify-end gap-3">
                  <button
                    onClick={closeDeleteModal}
                    className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
                  >
                    {'\u041e\u0442\u043c\u0435\u043d\u0430'}
                  </button>
                  <button
                    onClick={confirmDelete}
                    disabled={deleting}
                    className="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors"
                  >
                    {deleting ? '\u0423\u0434\u0430\u043b\u0435\u043d\u0438\u0435...' : '\u0423\u0434\u0430\u043b\u0438\u0442\u044c'}
                  </button>
                </div>
              </>
            )}

            {deleteModalType === 'confirm' && (
              <>
                <h3 className="text-lg font-bold mb-2">{'\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0441\u0435\u0437\u043e\u043d?'}</h3>
                <p className="text-sm text-gray-400 mb-6">
                  {'\u0412\u044b \u0443\u0432\u0435\u0440\u0435\u043d\u044b, \u0447\u0442\u043e \u0445\u043e\u0442\u0438\u0442\u0435 \u0443\u0434\u0430\u043b\u0438\u0442\u044c \u0441\u0435\u0437\u043e\u043d \u00ab'}{deletingItem.name}{'\u00bb? \u042d\u0442\u043e \u043c\u044f\u0433\u043a\u043e\u0435 \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u0435.'}
                </p>
                <div className="flex justify-end gap-3">
                  <button
                    onClick={closeDeleteModal}
                    className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
                  >
                    {'\u041e\u0442\u043c\u0435\u043d\u0430'}
                  </button>
                  <button
                    onClick={confirmDelete}
                    disabled={deleting}
                    className="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors"
                  >
                    {deleting ? '\u0423\u0434\u0430\u043b\u0435\u043d\u0438\u0435...' : '\u0423\u0434\u0430\u043b\u0438\u0442\u044c'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}