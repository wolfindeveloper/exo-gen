import { useCallback, useEffect, useState } from 'react'
import { Pencil, Plus, Trash2, X } from 'lucide-react'

import { api } from '../../api/client'
import type { AdminStarsPackage } from '../../types'

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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [forbidden, setForbidden] = useState(false)

  const [showForm, setShowForm] = useState(false)
  const [editingItem, setEditingItem] = useState<AdminStarsPackage | null>(null)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)

  const [deletingItem, setDeletingItem] = useState<AdminStarsPackage | null>(null)
  const [deleting, setDeleting] = useState(false)

  const loadItems = useCallback(async () => {
    try {
      setLoading(true)
      setForbidden(false)
      setError(null)
      const data = await api.getStarsPackages()
      setPackages(data)
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
      await loadItems()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = (item: AdminStarsPackage) => {
    setDeletingItem(item)
  }

  const confirmDelete = async () => {
    if (!deletingItem) return
    try {
      setDeleting(true)
      await api.deleteAdminStarsPackage(deletingItem.id)
      setDeletingItem(null)
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
          <p className="text-sm text-gray-500">{'\u0412\u0441\u0435\u0433\u043e:'} {packages.length}</p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
        >
          <Plus size={18} />
          {'\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043f\u0430\u043a\u0435\u0442'}
        </button>
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
          {'\u041f\u0430\u043a\u0435\u0442\u043e\u0432 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442. \u0421\u043e\u0437\u0434\u0430\u0439\u0442\u0435 \u043f\u0435\u0440\u0432\u044b\u0439!'}
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg overflow-x-auto">
          <table className="w-full text-sm min-w-[480px]">
            <thead>
              <tr className="bg-gray-750 border-b border-gray-700 text-left text-gray-400">
                <th className="px-3 py-3 font-medium">{'\u0426\u0435\u043d\u0430 (Stars)'}</th>
                <th className="px-3 py-3 font-medium">{'\u041d\u0430\u0433\u0440\u0430\u0434\u0430 (XGen)'}</th>
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