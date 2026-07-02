import { useCallback, useEffect, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight, Info, Package, PackageOpen, Pencil, Plus, Search, Trash2, X } from 'lucide-react'

import { api } from '../../api/client'
import type { AdminItem, AdminShopItem } from '../../types'

const PAGE_SIZE = 20

const SORT_OPTIONS: { value: string; label: string }[] = [
  { value: 'price_xgen', label: 'По цене' },
  { value: 'daily_limit', label: 'По дневному лимиту' },
  { value: 'stock_limit', label: 'По запасу' },
]

interface BundleFormItem {
  item_id: string
  quantity: number
}

interface FormState {
  mode: 'single' | 'bundle'
  item_id: string
  bundle_items: BundleFormItem[]
  price_xgen: string
  daily_limit: string
  stock_limit: string
  is_active: boolean
}

const EMPTY_FORM: FormState = {
  mode: 'single',
  item_id: '',
  bundle_items: [],
  price_xgen: '0',
  daily_limit: '0',
  stock_limit: '0',
  is_active: true,
}

export function ShopManager() {
  const [shopItems, setShopItems] = useState<AdminShopItem[]>([])
  const [allItems, setAllItems] = useState<AdminItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [forbidden, setForbidden] = useState(false)

  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [sortBy, setSortBy] = useState<string>('price_xgen')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const [showForm, setShowForm] = useState(false)
  const [editingItem, setEditingItem] = useState<AdminShopItem | null>(null)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)

  const [deletingItem, setDeletingItem] = useState<AdminShopItem | null>(null)
  const [deleting, setDeleting] = useState(false)

  const [bundleItemSelect, setBundleItemSelect] = useState('')
  const [bundleItemQty, setBundleItemQty] = useState(1)

  const searchTimer = useRef<ReturnType<typeof setTimeout>>()
  const itemNameMap = useRef<Map<string, string>>(new Map())

  useEffect(() => {
    const map = new Map<string, string>()
    for (const item of allItems) {
      map.set(item.id, item.name)
    }
    itemNameMap.current = map
  }, [allItems])

  const loadItems = useCallback(async () => {
    try {
      setLoading(true)
      setForbidden(false)
      setError(null)

      const [shopData, itemsData] = await Promise.all([
        api.getAdminShopItems(),
        api.getAdminItems(1, 500),
      ])

      setShopItems(shopData)
      setAllItems(itemsData.items)
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

  const filtered = shopItems.filter((item) => {
    if (!search) return true
    const q = search.toLowerCase()
    if (item.item_id) {
      const itemName = itemNameMap.current.get(item.item_id)
      if (itemName && itemName.toLowerCase().includes(q)) return true
    }
    if (item.id.toLowerCase().includes(q)) return true
    return false
  })

  const sorted = [...filtered].sort((a, b) => {
    let cmp = 0
    if (sortBy === 'price_xgen') cmp = a.price_xgen - b.price_xgen
    else if (sortBy === 'daily_limit') cmp = a.daily_limit - b.daily_limit
    else if (sortBy === 'stock_limit') cmp = a.stock_limit - b.stock_limit
    return sortOrder === 'asc' ? cmp : -cmp
  })

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE) || 1
  const paged = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const getItemDisplay = (item: AdminShopItem): string => {
    if (item.item_id) {
      return itemNameMap.current.get(item.item_id) || `ID: ${item.item_id.slice(0, 8)}...`
    }
    if (item.bundle_items?.length) {
      return `\u0411\u0430\u043d\u0434\u043b (${item.bundle_items.length} \u043f\u0440\u0435\u0434\u043c\u0435\u0442\u043e\u0432)`
    }
    return '\u2014'
  }

  const getItemShortDisplay = (itemId: string): string => {
    return itemNameMap.current.get(itemId) || `ID: ${itemId.slice(0, 8)}...`
  }

  const openCreate = () => {
    setEditingItem(null)
    setForm(EMPTY_FORM)
    setBundleItemSelect('')
    setBundleItemQty(1)
    setShowForm(true)
  }

  const openEdit = (item: AdminShopItem) => {
    setEditingItem(item)
    const isBundle = !item.item_id && item.bundle_items?.length > 0
    setForm({
      mode: isBundle ? 'bundle' : 'single',
      item_id: item.item_id || '',
      bundle_items: (item.bundle_items || []).map((b) => ({
        item_id: b.item_id,
        quantity: b.quantity,
      })),
      price_xgen: String(item.price_xgen),
      daily_limit: String(item.daily_limit),
      stock_limit: String(item.stock_limit),
      is_active: item.is_active,
    })
    setBundleItemSelect('')
    setBundleItemQty(1)
    setShowForm(true)
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingItem(null)
    setForm(EMPTY_FORM)
  }

  const addBundleItem = () => {
    if (!bundleItemSelect) return
    if (form.bundle_items.some((b) => b.item_id === bundleItemSelect)) return
    setForm({
      ...form,
      bundle_items: [...form.bundle_items, { item_id: bundleItemSelect, quantity: bundleItemQty }],
    })
    setBundleItemSelect('')
    setBundleItemQty(1)
  }

  const removeBundleItem = (idx: number) => {
    setForm({
      ...form,
      bundle_items: form.bundle_items.filter((_, i) => i !== idx),
    })
  }

  const handleSubmit = async () => {
    if (form.mode === 'single' && !form.item_id) {
      setError('\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0440\u0435\u0434\u043c\u0435\u0442 \u0434\u043b\u044f \u043f\u0440\u043e\u0434\u0430\u0436\u0438')
      return
    }
    if (form.mode === 'bundle' && form.bundle_items.length === 0) {
      setError('\u0414\u043e\u0431\u0430\u0432\u044c\u0442\u0435 \u0445\u043e\u0442\u044f \u0431\u044b \u043e\u0434\u0438\u043d \u043f\u0440\u0435\u0434\u043c\u0435\u0442 \u0432 \u0431\u0430\u043d\u0434\u043b')
      return
    }

    try {
      setSubmitting(true)
      setError(null)

      const limit = (v: string) => parseInt(v) || 0

      if (editingItem) {
        const payload: Record<string, unknown> = {
          price_xgen: limit(form.price_xgen),
          daily_limit: limit(form.daily_limit),
          stock_limit: limit(form.stock_limit),
          is_active: form.is_active,
        }

        if (form.mode === 'bundle') {
          payload.bundle_items = form.bundle_items
        }

        await api.updateAdminShopItem(editingItem.id, payload)
      } else {
        const payload: Record<string, unknown> = {
          price_xgen: limit(form.price_xgen),
          daily_limit: limit(form.daily_limit),
          stock_limit: limit(form.stock_limit),
          is_active: form.is_active,
        }

        if (form.mode === 'single') {
          payload.item_id = form.item_id
        } else {
          payload.bundle_items = form.bundle_items
        }

        await api.createAdminShopItem(payload as any)
      }

      closeForm()
      await loadItems()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  const confirmDelete = async () => {
    if (!deletingItem) return
    try {
      setDeleting(true)
      await api.deleteAdminShopItem(deletingItem.id)
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

  const itemsForSelect = allItems.filter(
    (it) => !form.bundle_items.some((b) => b.item_id === it.id),
  )

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-xl font-bold">{'\u041c\u0430\u0433\u0430\u0437\u0438\u043d'}</h2>
          <p className="text-sm text-gray-500">{'\u0412\u0441\u0435\u0433\u043e \u0442\u043e\u0432\u0430\u0440\u043e\u0432:'} {shopItems.length}</p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
        >
          <Plus size={18} />
          {'\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0442\u043e\u0432\u0430\u0440'}
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-2 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => handleSearchInput(e.target.value)}
            placeholder={'\u041f\u043e\u0438\u0441\u043a \u043f\u043e \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u044e \u043f\u0440\u0435\u0434\u043c\u0435\u0442\u0430...'}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
          />
        </div>
        <select
          value={sortBy}
          onChange={(e) => { setSortBy(e.target.value); setPage(1) }}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
        >
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
      ) : paged.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-500">
          {search ? '\u041d\u0438\u0447\u0435\u0433\u043e \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e' : '\u0412 \u043c\u0430\u0433\u0430\u0437\u0438\u043d\u0435 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442 \u0442\u043e\u0432\u0430\u0440\u043e\u0432. \u0414\u043e\u0431\u0430\u0432\u044c\u0442\u0435 \u043f\u0435\u0440\u0432\u044b\u0439!'}
        </div>
      ) : (
        <>
          <div className="bg-gray-800 rounded-lg overflow-x-auto mb-4">
            <table className="w-full text-sm min-w-[640px]">
              <thead>
                <tr className="bg-gray-750 border-b border-gray-700 text-left text-gray-400">
                  <th className="px-3 py-3 font-medium">{'\u0422\u043e\u0432\u0430\u0440'}</th>
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('price_xgen')}>
                    {'\u0426\u0435\u043d\u0430 (XGen)'}{sortIcon('price_xgen')}
                  </th>
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('daily_limit')}>
                    {'\u041b\u0438\u043c\u0438\u0442/\u0434\u0435\u043d\u044c'}{sortIcon('daily_limit')}
                  </th>
                  <th className="px-3 py-3 font-medium hidden sm:table-cell cursor-pointer select-none hover:text-white" onClick={() => handleSort('stock_limit')}>
                    {'\u0417\u0430\u043f\u0430\u0441'}{sortIcon('stock_limit')}
                  </th>
                  <th className="px-3 py-3 font-medium hidden sm:table-cell">{'\u0421\u0442\u0430\u0442\u0443\u0441'}</th>
                  <th className="px-3 py-3 font-medium text-center">
                    <span className="flex items-center gap-1 justify-center">
                      <Info size={14} />
                      {'\u041f\u043e\u043a\u0443\u043f\u043e\u043a'}
                    </span>
                  </th>
                  <th className="px-3 py-3 font-medium text-right">{'\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u044f'}</th>
                </tr>
              </thead>
              <tbody>
                {paged.map((item) => (
                  <tr key={item.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                    <td className="px-3 py-3 font-medium text-white">
                      <div className="flex items-center gap-2">
                        {item.item_id ? (
                          <Package size={16} className="text-blue-400 shrink-0" />
                        ) : (
                          <PackageOpen size={16} className="text-amber-400 shrink-0" />
                        )}
                        {getItemDisplay(item)}
                      </div>
                    </td>
                    <td className="px-3 py-3 text-cyan-400 font-medium">{item.price_xgen.toLocaleString()}</td>
                    <td className="px-3 py-3 text-gray-400">{item.daily_limit === 0 ? '\u221e' : item.daily_limit}</td>
                    <td className="px-3 py-3 text-gray-400 hidden sm:table-cell">{item.stock_limit === 0 ? '\u221e' : item.stock_limit}</td>
                    <td className="px-3 py-3 hidden sm:table-cell">
                      {item.is_active ? (
                        <span className="text-green-400 text-xs">{'\u0410\u043a\u0442\u0438\u0432\u0435\u043d'}</span>
                      ) : (
                        <span className="text-red-400 text-xs">{'\u041d\u0435\u0430\u043a\u0442\u0438\u0432\u0435\u043d'}</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-center">
                      <span className="text-gray-300 font-medium">{item.analytics.total_purchases}</span>
                      <span className="text-xs text-gray-600 ml-1">
                        / {item.analytics.today_purchases} today
                      </span>
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
                          onClick={() => setDeletingItem(item)}
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
                {editingItem ? '\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0442\u043e\u0432\u0430\u0440' : '\u041d\u043e\u0432\u044b\u0439 \u0442\u043e\u0432\u0430\u0440'}
              </h3>
              <button onClick={closeForm} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-4">
              {!editingItem && (
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{'\u0422\u0438\u043f \u0442\u043e\u0432\u0430\u0440\u0430'}</label>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setForm({ ...form, mode: 'single', item_id: '', bundle_items: [] })}
                      className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                        form.mode === 'single'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-700 text-gray-400 hover:text-white'
                      }`}
                    >
                      <Package size={16} />
                      {'\u041e\u0434\u0438\u043d\u043e\u0447\u043d\u044b\u0439 \u043f\u0440\u0435\u0434\u043c\u0435\u0442'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setForm({ ...form, mode: 'bundle', item_id: '', bundle_items: [] })}
                      className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                        form.mode === 'bundle'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-700 text-gray-400 hover:text-white'
                      }`}
                    >
                      <PackageOpen size={16} />
                      {'\u041d\u0430\u0431\u043e\u0440 (\u0411\u0430\u043d\u0434\u043b)'}
                    </button>
                  </div>
                </div>
              )}

              {editingItem && (
                <div className="flex items-center gap-2 text-sm text-gray-400 bg-gray-700/50 px-3 py-2 rounded-lg">
                  {form.mode === 'single' ? (
                    <><Package size={16} className="text-blue-400" /> {'\u041e\u0434\u0438\u043d\u043e\u0447\u043d\u044b\u0439 \u043f\u0440\u0435\u0434\u043c\u0435\u0442'}</>
                  ) : (
                    <><PackageOpen size={16} className="text-amber-400" /> {'\u041d\u0430\u0431\u043e\u0440 (\u0411\u0430\u043d\u0434\u043b)'}</>
                  )}
                </div>
              )}

              {form.mode === 'single' && (
                <div>
                  <label className="block text-sm text-gray-400 mb-1">
                    {editingItem ? '\u041f\u0440\u0435\u0434\u043c\u0435\u0442 (\u043d\u0435\u0438\u0437\u043c\u0435\u043d\u044f\u0435\u043c\u043e)' : '\u041f\u0440\u0435\u0434\u043c\u0435\u0442'}
                  </label>
                  {editingItem ? (
                    <div className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-gray-400 text-sm">
                      {getItemShortDisplay(form.item_id)}
                    </div>
                  ) : (
                    <select
                      value={form.item_id}
                      onChange={(e) => setForm({ ...form, item_id: e.target.value })}
                      className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                    >
                      <option value="">{'\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0440\u0435\u0434\u043c\u0435\u0442...'}</option>
                      {allItems.map((it) => (
                        <option key={it.id} value={it.id}>
                          {it.name} ({it.type}, {it.rarity})
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}

              {form.mode === 'bundle' && (
                <div>
                  <label className="block text-sm text-gray-400 mb-2">{'\u041f\u0440\u0435\u0434\u043c\u0435\u0442\u044b \u0432 \u0431\u0430\u043d\u0434\u043b\u0435'}</label>

                  {form.bundle_items.length === 0 && (
                    <p className="text-xs text-gray-600 mb-2">{'\u041d\u0435\u0442 \u043f\u0440\u0435\u0434\u043c\u0435\u0442\u043e\u0432. \u0414\u043e\u0431\u0430\u0432\u044c\u0442\u0435 \u0445\u043e\u0442\u044f \u0431\u044b \u043e\u0434\u0438\u043d.'}</p>
                  )}

                  <div className="space-y-2 mb-3">
                    {form.bundle_items.map((b, idx) => (
                      <div key={idx} className="flex items-center gap-2 bg-gray-900 rounded-lg px-3 py-2">
                        <span className="flex-1 text-sm text-white truncate">
                          {getItemShortDisplay(b.item_id)}
                        </span>
                        <span className="text-xs text-gray-400">x{b.quantity}</span>
                        <button
                          onClick={() => removeBundleItem(idx)}
                          className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ))}
                  </div>

                  <div className="flex items-end gap-2">
                    <div className="flex-1">
                      <label className="block text-xs text-gray-500 mb-1">{'\u041f\u0440\u0435\u0434\u043c\u0435\u0442'}</label>
                      <select
                        value={bundleItemSelect}
                        onChange={(e) => setBundleItemSelect(e.target.value)}
                        className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 outline-none"
                      >
                        <option value="">{'\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435...'}</option>
                        {itemsForSelect.map((it) => (
                          <option key={it.id} value={it.id}>
                            {it.name} ({it.type}, {it.rarity})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="w-20">
                      <label className="block text-xs text-gray-500 mb-1">{'\u041a\u043e\u043b-\u0432\u043e'}</label>
                      <input
                        type="number"
                        min={1}
                        value={bundleItemQty}
                        onChange={(e) => setBundleItemQty(Math.max(1, parseInt(e.target.value) || 1))}
                        className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 outline-none"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={addBundleItem}
                      disabled={!bundleItemSelect}
                      className="bg-gray-700 hover:bg-gray-600 disabled:opacity-30 text-white px-3 py-2 rounded-lg text-sm transition-colors"
                    >
                      <Plus size={16} />
                    </button>
                  </div>
                </div>
              )}

              <hr className="border-gray-700" />

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{'\u0426\u0435\u043d\u0430 (XGen)'}</label>
                  <input
                    type="number"
                    min={0}
                    value={form.price_xgen}
                    onChange={(e) => setForm({ ...form, price_xgen: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{'\u0414\u043d\u0435\u0432\u043d\u043e\u0439 \u043b\u0438\u043c\u0438\u0442'} (0 = {'\u0431\u0435\u0437\u043b\u0438\u043c\u0438\u0442'})</label>
                  <input
                    type="number"
                    min={0}
                    value={form.daily_limit}
                    onChange={(e) => setForm({ ...form, daily_limit: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">{'\u041e\u0431\u0449\u0438\u0439 \u0437\u0430\u043f\u0430\u0441'} (0 = {'\u0431\u0435\u0437\u043b\u0438\u043c\u0438\u0442'})</label>
                  <input
                    type="number"
                    min={0}
                    value={form.stock_limit}
                    onChange={(e) => setForm({ ...form, stock_limit: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  />
                </div>
                <div className="flex items-end pb-2">
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
            <h3 className="text-lg font-bold mb-2">{'\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0442\u043e\u0432\u0430\u0440?'}</h3>
            <p className="text-sm text-gray-400 mb-6">
              {'\u0412\u044b \u0443\u0432\u0435\u0440\u0435\u043d\u044b, \u0447\u0442\u043e \u0445\u043e\u0442\u0438\u0442\u0435 \u0443\u0434\u0430\u043b\u0438\u0442\u044c \u044d\u0442\u043e\u0442 \u0442\u043e\u0432\u0430\u0440? \u042d\u0442\u043e \u043c\u044f\u0433\u043a\u043e\u0435 \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u0435, \u0442\u043e\u0432\u0430\u0440 \u043f\u043e\u043c\u0435\u0442\u0438\u0442\u0441\u044f \u043a\u0430\u043a \u0443\u0434\u0430\u043b\u0435\u043d\u043d\u044b\u0439.'}
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