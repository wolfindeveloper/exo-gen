import { useCallback, useEffect, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight, Pencil, Plus, Search, Trash2, X } from 'lucide-react'

import { api } from '../../api/client'
import type { AdminStarsPackage } from '../../types'

const PAGE_SIZE = 20

const SORT_OPTIONS: { value: string; label: string }[] = [
  { value: 'stars_amount', label: 'По цене (Stars)' },
  { value: 'xgen_reward', label: 'По награде (XGen)' },
]

interface FormState {
  stars_amount: string
  xgen_reward: string
  is_active: boolean
}

const EMPTY_FORM: FormState = {
  stars_amount: '',
  xgen_reward: '',
  is_active: true,
}

export function StarsPackagesManager() {
  const [packages, setPackages] = useState<AdminStarsPackage[]>([])
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
  const [editingItem, setEditingItem] = useState<AdminStarsPackage | null>(null)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)

  const [deletingItem, setDeletingItem] = useState<AdminStarsPackage | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  const searchTimer = useRef<ReturnType<typeof setTimeout>>(undefined)

  const loadItems = useCallback(async (p: number, s: string, sb?: string, so?: 'asc' | 'desc') => {
    try {
      setLoading(true)
      setForbidden(false)
      setError(null)
      const data = await api.getAdminStarsPackages(p, PAGE_SIZE, s || undefined, sb, so)
      setPackages(data.items)
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

  const openCreate = () => {
    setEditingItem(null)
    setForm(EMPTY_FORM)
    setShowForm(true)
  }

  const openEdit = (item: AdminStarsPackage) => {
    setEditingItem(item)
    setForm({
      stars_amount: String(item.stars_amount),
      xgen_reward: String(item.xgen_reward),
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
    const stars = parseInt(form.stars_amount)
    const xgen = parseInt(form.xgen_reward)

    if (!stars || stars <= 0) {
      setError('\u0426\u0435\u043d\u0430 \u0432 Stars \u0434\u043e\u043b\u0436\u043d\u0430 \u0431\u044b\u0442\u044c \u0431\u043e\u043b\u044c\u0448\u0435 0')
      return
    }
    if (!xgen || xgen <= 0) {
      setError('\u041d\u0430\u0433\u0440\u0430\u0434\u0430 XGen \u0434\u043e\u043b\u0436\u043d\u0430 \u0431\u044b\u0442\u044c \u0431\u043e\u043b\u044c\u0448\u0435 0')
      return
    }

    try {
      setSubmitting(true)
      setError(null)

      if (editingItem) {
        await api.updateAdminStarsPackage(editingItem.id, {
          stars_amount: stars,
          xgen_reward: xgen,
          is_active: form.is_active,
        })
      } else {
        await api.createAdminStarsPackage({
          stars_amount: stars,
          xgen_reward: xgen,
          is_active: form.is_active,
        })
      }

      closeForm()
      await loadItems(page, search, sortBy, sortOrder)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = (item: AdminStarsPackage) => {
    setDeletingItem(item)
    setDeleteError('')
  }

  const confirmDelete = async () => {
    if (!deletingItem) return
    try {
      setDeleting(true)
      setDeleteError('')
      await api.deleteAdminStarsPackage(deletingItem.id)
      setDeletingItem(null)
      await loadItems(page, search, sortBy, sortOrder)
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
          <h2 className="text-xl font-bold">{'\u041f\u0430\u043a\u0435\u0442\u044b Stars'}</h2>
          <p className="text-sm text-gray-500">{'\u0412\u0441\u0435\u0433\u043e:'} {total}</p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
        >
          <Plus size={18} />
          {'\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043f\u0430\u043a\u0435\u0442'}
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-2 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => handleSearchInput(e.target.value)}
            placeholder={'\u041f\u043e\u0438\u0441\u043a \u043f\u043e \u0446\u0435\u043d\u0435...'}
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
      ) : packages.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-500">
          {search ? '\u041d\u0438\u0447\u0435\u0433\u043e \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e' : '\u041f\u0430\u043a\u0435\u0442\u043e\u0432 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442. \u0421\u043e\u0437\u0434\u0430\u0439\u0442\u0435 \u043f\u0435\u0440\u0432\u044b\u0439!'}
        </div>
      ) : (
        <>
          <div className="bg-gray-800 rounded-lg overflow-x-auto mb-4">
            <table className="w-full text-sm min-w-[480px]">
              <thead>
                <tr className="bg-gray-750 border-b border-gray-700 text-left text-gray-400">
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('stars_amount')}>
                    {'\u0426\u0435\u043d\u0430 (Stars)'}{sortIcon('stars_amount')}
                  </th>
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('xgen_reward')}>
                    {'\u041d\u0430\u0433\u0440\u0430\u0434\u0430 (XGen)'}{sortIcon('xgen_reward')}
                  </th>
                  <th className="px-3 py-3 font-medium">{'\u0421\u0442\u0430\u0442\u0443\u0441'}</th>
                  <th className="px-3 py-3 font-medium text-right">{'\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u044f'}</th>
                </tr>
              </thead>
              <tbody>
                {packages.map((item) => (
                  <tr key={item.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                    <td className="px-3 py-3 font-medium text-white">{item.stars_amount.toLocaleString()}</td>
                    <td className="px-3 py-3 text-cyan-400 font-medium">{item.xgen_reward.toLocaleString()}</td>
                    <td className="px-3 py-3">
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
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-md max-h-[90vh] overflow-y-auto mx-4">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 sticky top-0 bg-gray-800 z-10">
              <h3 className="text-lg font-bold">
                {editingItem ? '\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043f\u0430\u043a\u0435\u0442' : '\u041d\u043e\u0432\u044b\u0439 \u043f\u0430\u043a\u0435\u0442'}
              </h3>
              <button onClick={closeForm} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">{'\u0426\u0435\u043d\u0430 (Telegram Stars)'}</label>
                <input
                  type="number"
                  min={1}
                  value={form.stars_amount}
                  onChange={(e) => setForm({ ...form, stars_amount: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  placeholder="100"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">{'\u041d\u0430\u0433\u0440\u0430\u0434\u0430 (XGen)'}</label>
                <input
                  type="number"
                  min={1}
                  value={form.xgen_reward}
                  onChange={(e) => setForm({ ...form, xgen_reward: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  placeholder="1000"
                />
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

      {deletingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setDeletingItem(null)} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-sm p-6">
            <h3 className="text-lg font-bold mb-2">{'\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u043f\u0430\u043a\u0435\u0442?'}</h3>
            <p className="text-sm text-gray-400 mb-6">
              {'\u0412\u044b \u0443\u0432\u0435\u0440\u0435\u043d\u044b, \u0447\u0442\u043e \u0445\u043e\u0442\u0438\u0442\u0435 \u0443\u0434\u0430\u043b\u0438\u0442\u044c \u044d\u0442\u043e\u0442 \u043f\u0430\u043a\u0435\u0442? \u042d\u0442\u043e \u043c\u044f\u0433\u043a\u043e\u0435 \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u0435.'}
            </p>
            {deleteError && <div className="mb-4 bg-red-900/30 border border-red-700/50 text-red-300 px-3 py-2 rounded-lg text-sm">{deleteError}</div>}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeletingItem(null)}
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
          </div>
        </div>
      )}
    </div>
  )
}
