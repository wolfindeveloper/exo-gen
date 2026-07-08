import { useCallback, useEffect, useRef, useState } from 'react'
import { ArrowLeft, ChevronLeft, ChevronRight, Pencil, Plus, Search, Trash2, X, GripHorizontal } from 'lucide-react'
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors, type DragEndEvent } from '@dnd-kit/core'
import { SortableContext, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { api } from '../../api/client'
import type { AdminChapter, AdminArticle, ChapterRewardItem, AdminSeason, AdminItem } from '../../types'

const PAGE_SIZE = 20

const SORT_OPTIONS: { value: string; label: string }[] = [
  { value: 'name', label: 'По названию' },
  { value: 'created_at', label: 'По дате создания' },
]

const TRIGGER_EVENT_TYPES = [
  'expedition_completed',
  'article_unlocked',
  'daily_login',
  'chapter_completed',
  'purchase_made',
  'stars_donated',
  'afk_seconds',
]

interface ChapterFormState {
  name: string
  description: string
  type: 'normal' | 'secret' | 'seasonal'
  season_id: string
  reward_xgen: string
  reward_fragments: string
  reward_items: ChapterRewardItem[]
}

const EMPTY_CHAPTER_FORM: ChapterFormState = {
  name: '',
  description: '',
  type: 'normal',
  season_id: '',
  reward_xgen: '0',
  reward_fragments: '0',
  reward_items: [],
}

interface ArticleFormState {
  title: string
  content: string
  unlock_type: 'fragments' | 'trigger' | 'item'
  fragment_cost: string
  trigger_event_type: string
  trigger_threshold: string
  required_item_id: string
}

const EMPTY_ARTICLE_FORM: ArticleFormState = {
  title: '',
  content: '',
  unlock_type: 'fragments',
  fragment_cost: '0',
  trigger_event_type: '',
  trigger_threshold: '1',
  required_item_id: '',
}

function SortableArticle({
  article,
  onEdit,
  onDelete,
}: {
  article: AdminArticle
  onEdit: (a: AdminArticle) => void
  onDelete: (a: AdminArticle) => void
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: article.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  }

  const unlockLabel = () => {
    if (article.required_item_id) return 'Предмет'
    if (article.trigger_event_type) return `Триггер: ${article.trigger_event_type}`
    if (article.fragment_cost > 0) return `${article.fragment_cost} фрагментов`
    return 'Бесплатно'
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex items-center gap-2 bg-gray-800 rounded-lg px-3 py-3 border border-gray-700/50 hover:border-gray-600 transition-colors"
    >
      <button
        className="cursor-grab active:cursor-grabbing text-gray-500 hover:text-gray-300 p-1 touch-none"
        {...attributes}
        {...listeners}
      >
        <GripHorizontal size={16} />
      </button>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-white font-medium truncate">{article.title}</p>
        <p className="text-xs text-gray-500 mt-0.5">{unlockLabel()}</p>
      </div>
      <button
        onClick={() => onEdit(article)}
        className="p-1.5 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors shrink-0"
        title="Редактировать"
      >
        <Pencil size={15} />
      </button>
      <button
        onClick={() => onDelete(article)}
        className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded transition-colors shrink-0"
        title="Удалить"
      >
        <Trash2 size={15} />
      </button>
    </div>
  )
}

export function ChaptersManager() {
  const [chapters, setChapters] = useState<AdminChapter[]>([])
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

  const [selectedChapter, setSelectedChapter] = useState<AdminChapter | null>(null)
  const selectedChapterIdRef = useRef<string | null>(null)

  const [showChapterForm, setShowChapterForm] = useState(false)
  const [editingChapter, setEditingChapter] = useState<AdminChapter | null>(null)
  const [chapterForm, setChapterForm] = useState<ChapterFormState>(EMPTY_CHAPTER_FORM)
  const [submittingChapter, setSubmittingChapter] = useState(false)

  const [showArticleForm, setShowArticleForm] = useState(false)
  const [editingArticle, setEditingArticle] = useState<AdminArticle | null>(null)
  const [articleForm, setArticleForm] = useState<ArticleFormState>(EMPTY_ARTICLE_FORM)
  const [submittingArticle, setSubmittingArticle] = useState(false)

  const [deletingChapter, setDeletingChapter] = useState<AdminChapter | null>(null)
  const [deletingArticle, setDeletingArticle] = useState<AdminArticle | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  const [seasons, setSeasons] = useState<AdminSeason[]>([])
  const [allItems, setAllItems] = useState<AdminItem[]>([])

  const [rewardItemSelect, setRewardItemSelect] = useState('')
  const [rewardItemQty, setRewardItemQty] = useState(1)

  const searchTimer = useRef<ReturnType<typeof setTimeout>>(undefined)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
  )

  const loadChapters = useCallback(async (p: number, s: string, sb?: string, so?: 'asc' | 'desc') => {
    try {
      setLoading(true)
      setForbidden(false)
      setError(null)
      const data = await api.getAdminChapters(p, PAGE_SIZE, s || undefined, sb, so)
      setChapters(data.items)
      setTotal(data.total)
      setTotalPages(data.total_pages)
      if (selectedChapterIdRef.current) {
        const updated = data.items.find((ch) => ch.id === selectedChapterIdRef.current)
        if (updated) setSelectedChapter(updated)
      }
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

  const loadReferenceData = useCallback(async () => {
    try {
      const [seasonsData, itemsData] = await Promise.all([
        api.getAdminSeasons(1, 200),
        api.getAdminItems(1, 200),
      ])
      setSeasons(seasonsData.items)
      setAllItems(itemsData.items)
    } catch {
      // non-critical
    }
  }, [])

  useEffect(() => {
    loadChapters(page, search, sortBy, sortOrder)
  }, [page, search, sortBy, sortOrder, loadChapters])

  useEffect(() => {
    loadReferenceData()
  }, [loadReferenceData])

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

  const chapterTypeLabel = (ch: AdminChapter) => {
    if (ch.season_id) return 'Сезонная'
    if (ch.is_secret) return 'Секретная'
    return 'Обычная'
  }

  const getSeasonName = (seasonId: string | null) => {
    if (!seasonId) return null
    return seasons.find((s) => s.id === seasonId)?.name || `ID: ${seasonId.slice(0, 8)}...`
  }

  const getItemName = (itemId: string | null) => {
    if (!itemId) return null
    return allItems.find((i) => i.id === itemId)?.name || `ID: ${itemId.slice(0, 8)}...`
  }

  // --- Chapter form ---

  const openCreateChapter = () => {
    setEditingChapter(null)
    setChapterForm(EMPTY_CHAPTER_FORM)
    setRewardItemSelect('')
    setRewardItemQty(1)
    setShowChapterForm(true)
  }

  const openEditChapter = (ch: AdminChapter) => {
    setEditingChapter(ch)
    setChapterForm({
      name: ch.name,
      description: ch.description,
      type: ch.season_id ? 'seasonal' : ch.is_secret ? 'secret' : 'normal',
      season_id: ch.season_id || '',
      reward_xgen: String(ch.reward_xgen),
      reward_fragments: String(ch.reward_fragments),
      reward_items: (ch.reward_items || []).map((r) => ({ item_id: r.item_id, quantity: r.quantity })),
    })
    setRewardItemSelect('')
    setRewardItemQty(1)
    setShowChapterForm(true)
  }

  const closeChapterForm = () => {
    setShowChapterForm(false)
    setEditingChapter(null)
    setChapterForm(EMPTY_CHAPTER_FORM)
  }

  const addRewardItem = () => {
    if (!rewardItemSelect) return
    if (chapterForm.reward_items.some((r) => r.item_id === rewardItemSelect)) return
    setChapterForm({
      ...chapterForm,
      reward_items: [...chapterForm.reward_items, { item_id: rewardItemSelect, quantity: rewardItemQty }],
    })
    setRewardItemSelect('')
    setRewardItemQty(1)
  }

  const removeRewardItem = (idx: number) => {
    setChapterForm({
      ...chapterForm,
      reward_items: chapterForm.reward_items.filter((_, i) => i !== idx),
    })
  }

  const handleSubmitChapter = async () => {
    if (!chapterForm.name.trim() || !chapterForm.description.trim()) {
      setError('Название и описание обязательны')
      return
    }
    if (chapterForm.type === 'seasonal' && !chapterForm.season_id) {
      setError('Выберите сезон для сезонной главы')
      return
    }

    try {
      setSubmittingChapter(true)
      setError(null)

      const payload: Record<string, unknown> = {
        name: chapterForm.name,
        description: chapterForm.description,
        reward_xgen: parseInt(chapterForm.reward_xgen) || 0,
        reward_fragments: parseInt(chapterForm.reward_fragments) || 0,
        reward_items: chapterForm.reward_items,
      }

      if (editingChapter) {
        if (chapterForm.type !== 'seasonal') {
          payload.is_secret = chapterForm.type === 'secret'
        }
        await api.updateAdminChapter(editingChapter.id, payload)
      } else {
        payload.is_secret = chapterForm.type === 'secret' || chapterForm.type === 'seasonal'
        payload.season_id = chapterForm.type === 'seasonal' ? chapterForm.season_id : null
        await api.createAdminChapter(payload as { name: string; description: string; is_secret?: boolean; season_id?: string | null; reward_xgen?: number; reward_fragments?: number; reward_items?: ChapterRewardItem[] })
      }

      closeChapterForm()
      await loadChapters(page, search, sortBy, sortOrder)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmittingChapter(false)
    }
  }

  const handleDeleteChapter = (ch: AdminChapter) => {
    setDeletingChapter(ch)
    setDeleteError('')
  }

  const confirmDeleteChapter = async () => {
    if (!deletingChapter) return
    try {
      setDeleting(true)
      setDeleteError('')
      await api.deleteAdminChapter(deletingChapter.id)
      if (selectedChapter?.id === deletingChapter.id) {
        setSelectedChapter(null)
        selectedChapterIdRef.current = null
      }
      setDeletingChapter(null)
      await loadChapters(page, search, sortBy, sortOrder)
    } catch (e) {
      setDeleteError((e as Error).message)
    } finally {
      setDeleting(false)
    }
  }

  // --- Article detail view ---

  const openChapterArticles = (ch: AdminChapter) => {
    setSelectedChapter(ch)
    selectedChapterIdRef.current = ch.id
  }

  const closeChapterArticles = () => {
    setSelectedChapter(null)
    selectedChapterIdRef.current = null
  }

  // --- Article form ---

  const openCreateArticle = () => {
    setEditingArticle(null)
    setArticleForm(EMPTY_ARTICLE_FORM)
    setShowArticleForm(true)
  }

  const openEditArticle = (a: AdminArticle) => {
    const unlockType = a.required_item_id ? 'item' : a.trigger_event_type ? 'trigger' : 'fragments'
    setEditingArticle(a)
    setArticleForm({
      title: a.title,
      content: a.content || '',
      unlock_type: unlockType as 'fragments' | 'trigger' | 'item',
      fragment_cost: String(a.fragment_cost || 0),
      trigger_event_type: a.trigger_event_type || '',
      trigger_threshold: String(a.trigger_threshold || 1),
      required_item_id: a.required_item_id || '',
    })
    setShowArticleForm(true)
  }

  const closeArticleForm = () => {
    setShowArticleForm(false)
    setEditingArticle(null)
    setArticleForm(EMPTY_ARTICLE_FORM)
  }

  const handleSubmitArticle = async () => {
    if (!articleForm.title.trim() || !articleForm.content.trim()) {
      setError('Название и содержание обязательны')
      return
    }
    if (articleForm.unlock_type === 'item' && !articleForm.required_item_id) {
      setError('Выберите ключевой предмет')
      return
    }
    if (articleForm.unlock_type === 'trigger') {
      if (!articleForm.trigger_event_type) {
        setError('Выберите тип триггера')
        return
      }
    }

    try {
      setSubmittingArticle(true)
      setError(null)

      const payload: Record<string, unknown> = {
        title: articleForm.title,
        content: articleForm.content,
      }

      if (articleForm.unlock_type === 'fragments') {
        payload.fragment_cost = parseInt(articleForm.fragment_cost) || 0
        payload.trigger_event_type = null
        payload.required_item_id = null
      } else if (articleForm.unlock_type === 'trigger') {
        payload.fragment_cost = 0
        payload.trigger_event_type = articleForm.trigger_event_type
        payload.trigger_threshold = parseInt(articleForm.trigger_threshold) || 1
        payload.required_item_id = null
      } else {
        payload.fragment_cost = 0
        payload.trigger_event_type = null
        payload.required_item_id = articleForm.required_item_id
      }

      if (editingArticle) {
        await api.updateAdminArticle(editingArticle.id, payload)
      } else {
        payload.chapter_id = selectedChapter!.id
        await api.createAdminArticle(payload as { chapter_id: string; title: string; content: string; fragment_cost?: number; trigger_event_type?: string | null; trigger_threshold?: number; required_item_id?: string | null })
      }

      closeArticleForm()
      await loadChapters(page, search, sortBy, sortOrder)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSubmittingArticle(false)
    }
  }

  const handleDeleteArticle = (a: AdminArticle) => {
    setDeletingArticle(a)
    setDeleteError('')
  }

  const confirmDeleteArticle = async () => {
    if (!deletingArticle) return
    try {
      setDeleting(true)
      setDeleteError('')
      await api.deleteAdminArticle(deletingArticle.id)
      setDeletingArticle(null)
      await loadChapters(page, search, sortBy, sortOrder)
    } catch (e) {
      setDeleteError((e as Error).message)
    } finally {
      setDeleting(false)
    }
  }

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id) return
    if (!selectedChapter) return

    const articles = selectedChapter.articles
    const oldIndex = articles.findIndex((a) => a.id === active.id)
    const newIndex = articles.findIndex((a) => a.id === over.id)
    if (oldIndex === -1 || newIndex === -1) return

    const reordered = [...articles]
    const [moved] = reordered.splice(oldIndex, 1)
    reordered.splice(newIndex, 0, moved)

    setSelectedChapter({ ...selectedChapter, articles: reordered })

    try {
      await api.reorderChapterArticles(selectedChapter.id, reordered.map((a) => a.id))
    } catch (e) {
      setError((e as Error).message)
      await loadChapters(page, search, sortBy, sortOrder)
    }
  }

  const itemsForRewardSelect = allItems.filter(
    (it) => !chapterForm.reward_items.some((r) => r.item_id === it.id),
  )

  const keyItemsForSelect = allItems.filter((it) => it.type === 'key_item')

  if (forbidden) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-2xl mb-2">{'\uD83D\uDD12'}</p>
          <p className="text-red-400 text-lg font-medium">Доступ запрещен. Вы не являетесь администратором.</p>
        </div>
      </div>
    )
  }

  // --- Detail view: articles for selected chapter ---
  if (selectedChapter) {
    return (
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={closeChapterArticles}
              className="flex items-center gap-1 text-sm text-gray-400 hover:text-white bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg transition-colors shrink-0"
            >
              <ArrowLeft size={16} />
              Назад
            </button>
            <div className="min-w-0">
              <h2 className="text-xl font-bold truncate">{selectedChapter.name}</h2>
              <p className="text-xs text-gray-500">{selectedChapter.articles.length} статей</p>
            </div>
          </div>
          <button
            onClick={openCreateArticle}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm shrink-0"
          >
            <Plus size={18} />
            Создать статью
          </button>
        </div>

        {error && (
          <div className="mb-4 bg-red-900/30 border border-red-700/50 text-red-300 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {selectedChapter.articles.length === 0 ? (
          <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-500">
            В этой главе пока нет статей. Создайте первую!
          </div>
        ) : (
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
            <SortableContext items={selectedChapter.articles.map((a) => a.id)} strategy={verticalListSortingStrategy}>
              <div className="space-y-2">
                {selectedChapter.articles.map((article) => (
                  <SortableArticle
                    key={article.id}
                    article={article}
                    onEdit={openEditArticle}
                    onDelete={handleDeleteArticle}
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        )}

        {/* Article Form Modal */}
        {showArticleForm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={closeArticleForm} />
            <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-lg max-h-[90vh] overflow-y-auto mx-4">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 sticky top-0 bg-gray-800 z-10">
                <h3 className="text-lg font-bold">
                  {editingArticle ? 'Редактировать статью' : 'Новая статья'}
                </h3>
                <button onClick={closeArticleForm} className="text-gray-400 hover:text-white">
                  <X size={20} />
                </button>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Название</label>
                  <input
                    type="text"
                    value={articleForm.title}
                    onChange={(e) => setArticleForm({ ...articleForm, title: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                    placeholder="Заголовок статьи"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-1">Содержание (Markdown)</label>
                  <textarea
                    value={articleForm.content}
                    onChange={(e) => setArticleForm({ ...articleForm, content: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none resize-none font-mono text-sm"
                    rows={6}
                    placeholder="Текст статьи в формате Markdown..."
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">Тип разблокировки</label>
                  <div className="flex flex-col gap-2">
                    <label className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition-colors ${
                      articleForm.unlock_type === 'fragments'
                        ? 'border-blue-500 bg-blue-900/20 text-white'
                        : 'border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-600'
                    }`}>
                      <input
                        type="radio"
                        name="unlock_type"
                        value="fragments"
                        checked={articleForm.unlock_type === 'fragments'}
                        onChange={() => setArticleForm({ ...articleForm, unlock_type: 'fragments' })}
                        className="accent-blue-500"
                      />
                      <div>
                        <span className="font-medium">За фрагменты</span>
                        <p className="text-xs text-gray-500 mt-0.5">Игрок платит фрагментами знаний</p>
                      </div>
                    </label>

                    <label className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition-colors ${
                      articleForm.unlock_type === 'trigger'
                        ? 'border-blue-500 bg-blue-900/20 text-white'
                        : 'border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-600'
                    }`}>
                      <input
                        type="radio"
                        name="unlock_type"
                        value="trigger"
                        checked={articleForm.unlock_type === 'trigger'}
                        onChange={() => setArticleForm({ ...articleForm, unlock_type: 'trigger' })}
                        className="accent-blue-500"
                      />
                      <div>
                        <span className="font-medium">За триггер</span>
                        <p className="text-xs text-gray-500 mt-0.5">Открывается при выполнении условия</p>
                      </div>
                    </label>

                    <label className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition-colors ${
                      articleForm.unlock_type === 'item'
                        ? 'border-blue-500 bg-blue-900/20 text-white'
                        : 'border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-600'
                    }`}>
                      <input
                        type="radio"
                        name="unlock_type"
                        value="item"
                        checked={articleForm.unlock_type === 'item'}
                        onChange={() => setArticleForm({ ...articleForm, unlock_type: 'item' })}
                        className="accent-blue-500"
                      />
                      <div>
                        <span className="font-medium">За предмет</span>
                        <p className="text-xs text-gray-500 mt-0.5">Требуется ключевой предмет в инвентаре</p>
                      </div>
                    </label>
                  </div>
                </div>

                {articleForm.unlock_type === 'fragments' && (
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Стоимость (фрагменты)</label>
                    <input
                      type="number"
                      min={1}
                      value={articleForm.fragment_cost}
                      onChange={(e) => setArticleForm({ ...articleForm, fragment_cost: e.target.value })}
                      className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                    />
                  </div>
                )}

                {articleForm.unlock_type === 'trigger' && (
                  <>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Тип события</label>
                      <select
                        value={articleForm.trigger_event_type}
                        onChange={(e) => setArticleForm({ ...articleForm, trigger_event_type: e.target.value })}
                        className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                      >
                        <option value="">Выберите триггер...</option>
                        {TRIGGER_EVENT_TYPES.map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Порог срабатывания</label>
                      <input
                        type="number"
                        min={1}
                        value={articleForm.trigger_threshold}
                        onChange={(e) => setArticleForm({ ...articleForm, trigger_threshold: e.target.value })}
                        className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                      />
                      <p className="text-xs text-gray-600 mt-1">Сколько раз должно произойти событие для открытия</p>
                    </div>
                  </>
                )}

                {articleForm.unlock_type === 'item' && (
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Ключевой предмет</label>
                    <select
                      value={articleForm.required_item_id}
                      onChange={(e) => setArticleForm({ ...articleForm, required_item_id: e.target.value })}
                      className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                    >
                      <option value="">Выберите предмет...</option>
                      {keyItemsForSelect.map((it) => (
                        <option key={it.id} value={it.id}>
                          {it.name} ({it.rarity})
                        </option>
                      ))}
                    </select>
                    {keyItemsForSelect.length === 0 && (
                      <p className="text-xs text-amber-500 mt-1">Нет предметов с типом key_item. Создайте их в разделе "Предметы".</p>
                    )}
                  </div>
                )}
              </div>

              <div className="px-6 py-4 border-t border-gray-700 flex justify-end gap-3 sticky bottom-0 bg-gray-800">
                <button
                  onClick={closeArticleForm}
                  className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleSubmitArticle}
                  disabled={submittingArticle}
                  className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors"
                >
                  {submittingArticle ? 'Сохранение...' : editingArticle ? 'Сохранить' : 'Создать'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Article Modal */}
        {deletingArticle && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setDeletingArticle(null)} />
            <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-sm p-6">
              <h3 className="text-lg font-bold mb-2">Удалить статью?</h3>
              <p className="text-sm text-gray-400 mb-6">
                Вы уверены, что хотите удалить статью «{deletingArticle.title}»? Это мягкое удаление. Статья не удалится, если её уже открыл хотя бы один игрок.
              </p>
              {deleteError && <div className="mb-4 bg-red-900/30 border border-red-700/50 text-red-300 px-3 py-2 rounded-lg text-sm">{deleteError}</div>}
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setDeletingArticle(null)}
                  className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={confirmDeleteArticle}
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

  // --- List view: all chapters ---
  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-xl font-bold">Главы Путеводителя</h2>
          <p className="text-sm text-gray-500">Всего: {total}</p>
        </div>
        <button
          onClick={openCreateChapter}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
        >
          <Plus size={18} />
          Создать главу
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-2 mb-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => handleSearchInput(e.target.value)}
            placeholder="Поиск по названию..."
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
      ) : chapters.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center text-gray-500">
          {search ? 'Ничего не найдено' : 'Глав пока нет. Создайте первую!'}
        </div>
      ) : (
        <>
          <div className="bg-gray-800 rounded-lg overflow-x-auto mb-4">
            <table className="w-full text-sm min-w-[600px]">
              <thead>
                <tr className="bg-gray-750 border-b border-gray-700 text-left text-gray-400">
                  <th className="px-3 py-3 font-medium cursor-pointer select-none hover:text-white" onClick={() => handleSort('name')}>
                    Название{sortIcon('name')}
                  </th>
                  <th className="px-3 py-3 font-medium">Тип</th>
                  <th className="px-3 py-3 font-medium hidden sm:table-cell">Сезон</th>
                  <th className="px-3 py-3 font-medium hidden sm:table-cell">Награды</th>
                  <th className="px-3 py-3 font-medium text-right">Действия</th>
                </tr>
              </thead>
              <tbody>
                {chapters.map((ch) => (
                  <tr key={ch.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                    <td className="px-3 py-3 font-medium text-white">
                      <div className="truncate max-w-[200px]">{ch.name}</div>
                    </td>
                    <td className="px-3 py-3">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        ch.season_id
                          ? 'bg-green-900/40 text-green-400'
                          : ch.is_secret
                            ? 'bg-purple-900/40 text-purple-400'
                            : 'bg-gray-700 text-gray-300'
                      }`}>
                        {chapterTypeLabel(ch)}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-gray-400 text-xs hidden sm:table-cell">
                      {getSeasonName(ch.season_id) || '\u2014'}
                    </td>
                    <td className="px-3 py-3 text-xs hidden sm:table-cell">
                      <div className="flex flex-wrap gap-1">
                        {ch.reward_xgen > 0 && <span className="text-cyan-400">{ch.reward_xgen} XGen</span>}
                        {ch.reward_fragments > 0 && <span className="text-purple-400">{ch.reward_fragments} Frags</span>}
                        {ch.reward_items?.length > 0 && (
                          <span className="text-amber-400">{ch.reward_items.length} предметов</span>
                        )}
                        {ch.reward_xgen === 0 && ch.reward_fragments === 0 && (!ch.reward_items || ch.reward_items.length === 0) && '\u2014'}
                      </div>
                    </td>
                    <td className="px-3 py-3">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => openChapterArticles(ch)}
                          className="px-2.5 py-1.5 text-xs text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors whitespace-nowrap"
                          title="Управление статьями"
                        >
                          Статьи ({ch.articles.length})
                        </button>
                        <button
                          onClick={() => openEditChapter(ch)}
                          className="p-1.5 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded transition-colors"
                          title="Редактировать"
                        >
                          <Pencil size={16} />
                        </button>
                        <button
                          onClick={() => handleDeleteChapter(ch)}
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

      {/* Chapter Form Modal */}
      {showChapterForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={closeChapterForm} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-lg max-h-[90vh] overflow-y-auto mx-4">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 sticky top-0 bg-gray-800 z-10">
              <h3 className="text-lg font-bold">
                {editingChapter ? 'Редактировать главу' : 'Новая глава'}
              </h3>
              <button onClick={closeChapterForm} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Название</label>
                <input
                  type="text"
                  value={chapterForm.name}
                  onChange={(e) => setChapterForm({ ...chapterForm, name: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  placeholder="Название главы"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Описание</label>
                <textarea
                  value={chapterForm.description}
                  onChange={(e) => setChapterForm({ ...chapterForm, description: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none resize-none"
                  rows={3}
                  placeholder="Описание главы"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Тип главы</label>
                <div className="flex flex-col gap-2">
                  <label className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition-colors ${
                    chapterForm.type === 'normal'
                      ? 'border-blue-500 bg-blue-900/20 text-white'
                      : 'border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-600'
                  }`}>
                    <input
                      type="radio"
                      name="chapter_type"
                      value="normal"
                      checked={chapterForm.type === 'normal'}
                      onChange={() => setChapterForm({ ...chapterForm, type: 'normal', season_id: '' })}
                      className="accent-blue-500"
                    />
                    <div>
                      <span className="font-medium">Обычная</span>
                      <p className="text-xs text-gray-500 mt-0.5">is_secret=false, season_id=null</p>
                    </div>
                  </label>

                  <label className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition-colors ${
                    chapterForm.type === 'secret'
                      ? 'border-blue-500 bg-blue-900/20 text-white'
                      : 'border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-600'
                  }`}>
                    <input
                      type="radio"
                      name="chapter_type"
                      value="secret"
                      checked={chapterForm.type === 'secret'}
                      onChange={() => setChapterForm({ ...chapterForm, type: 'secret', season_id: '' })}
                      className="accent-blue-500"
                    />
                    <div>
                      <span className="font-medium">Секретная</span>
                      <p className="text-xs text-gray-500 mt-0.5">is_secret=true, доступ только по триггерам</p>
                    </div>
                  </label>

                  <label className={`flex items-center gap-3 px-4 py-3 rounded-lg border cursor-pointer transition-colors ${
                    chapterForm.type === 'seasonal'
                      ? 'border-blue-500 bg-blue-900/20 text-white'
                      : 'border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-600'
                  }`}>
                    <input
                      type="radio"
                      name="chapter_type"
                      value="seasonal"
                      checked={chapterForm.type === 'seasonal'}
                      onChange={() => setChapterForm({ ...chapterForm, type: 'seasonal' })}
                      className="accent-blue-500"
                    />
                    <div>
                      <span className="font-medium">Сезонная</span>
                      <p className="text-xs text-gray-500 mt-0.5">season_id != null, привязка к сезону</p>
                    </div>
                  </label>
                </div>
              </div>

              {chapterForm.type === 'seasonal' && (
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Сезон</label>
                  <select
                    value={chapterForm.season_id}
                    onChange={(e) => setChapterForm({ ...chapterForm, season_id: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 outline-none"
                  >
                    <option value="">Выберите сезон...</option>
                    {seasons.map((s) => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <hr className="border-gray-700" />

              <div>
                <label className="block text-sm text-gray-400 mb-2">Награды за закрытие главы</label>
                <div className="grid grid-cols-2 gap-4 mb-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">reward_xgen</label>
                    <input
                      type="number"
                      min={0}
                      value={chapterForm.reward_xgen}
                      onChange={(e) => setChapterForm({ ...chapterForm, reward_xgen: e.target.value })}
                      className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">reward_fragments</label>
                    <input
                      type="number"
                      min={0}
                      value={chapterForm.reward_fragments}
                      onChange={(e) => setChapterForm({ ...chapterForm, reward_fragments: e.target.value })}
                      className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 outline-none"
                    />
                  </div>
                </div>

                <label className="block text-xs text-gray-500 mb-1.5">Предметы в награде (reward_items)</label>
                {chapterForm.reward_items.length === 0 && (
                  <p className="text-xs text-gray-600 mb-2">Нет предметов. Добавьте ниже.</p>
                )}
                <div className="space-y-2 mb-3">
                  {chapterForm.reward_items.map((r, idx) => (
                    <div key={idx} className="flex items-center gap-2 bg-gray-900 rounded-lg px-3 py-2">
                      <span className="flex-1 text-sm text-white truncate">
                        {getItemName(r.item_id)}
                      </span>
                      <span className="text-xs text-gray-400">x{r.quantity}</span>
                      <button
                        onClick={() => removeRewardItem(idx)}
                        className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>

                <div className="flex items-end gap-2">
                  <div className="flex-1">
                    <label className="block text-xs text-gray-500 mb-1">Предмет</label>
                    <select
                      value={rewardItemSelect}
                      onChange={(e) => setRewardItemSelect(e.target.value)}
                      className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 outline-none"
                    >
                      <option value="">Выберите...</option>
                      {itemsForRewardSelect.map((it) => (
                        <option key={it.id} value={it.id}>
                          {it.name} ({it.type}, {it.rarity})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="w-20">
                    <label className="block text-xs text-gray-500 mb-1">Кол-во</label>
                    <input
                      type="number"
                      min={1}
                      value={rewardItemQty}
                      onChange={(e) => setRewardItemQty(Math.max(1, parseInt(e.target.value) || 1))}
                      className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-blue-500 outline-none"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={addRewardItem}
                    disabled={!rewardItemSelect}
                    className="bg-gray-700 hover:bg-gray-600 disabled:opacity-30 text-white px-3 py-2 rounded-lg text-sm transition-colors"
                  >
                    <Plus size={16} />
                  </button>
                </div>
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-700 flex justify-end gap-3 sticky bottom-0 bg-gray-800">
              <button
                onClick={closeChapterForm}
                className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleSubmitChapter}
                disabled={submittingChapter}
                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors"
              >
                {submittingChapter ? 'Сохранение...' : editingChapter ? 'Сохранить' : 'Создать'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Chapter Modal */}
      {deletingChapter && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setDeletingChapter(null)} />
          <div className="relative bg-gray-800 rounded-xl border border-gray-700 w-full max-w-sm p-6">
            <h3 className="text-lg font-bold mb-2">Удалить главу?</h3>
            <p className="text-sm text-gray-400 mb-6">
              Вы уверены, что хотите удалить главу «{deletingChapter.name}»? Это мягкое удаление. Глава не удалится, если в ней есть статьи, открытые игроками.
            </p>
            {deleteError && <div className="mb-4 bg-red-900/30 border border-red-700/50 text-red-300 px-3 py-2 rounded-lg text-sm">{deleteError}</div>}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeletingChapter(null)}
                className="px-4 py-2 text-gray-400 hover:text-white text-sm transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={confirmDeleteChapter}
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
