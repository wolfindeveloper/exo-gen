import { useState, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FlaskConical, Gem, Zap, Trophy } from 'lucide-react'
import { useConfigStore } from '../store/useConfigStore'
import { usePlayerStore } from '../store/usePlayerStore'
import { craftArtifact, getArtifacts, stakeArtifact, unstakeArtifact, claimYield } from '../lib/api-helpers'
import { useToast, ToastContainer } from '../components/Toast'
import { Starfield } from '../components/Starfield'
import SubMenu from '../components/layout/SubMenu'
import WalletConnect from '../components/wallet/WalletConnect'
import { DiscoverersList } from '../components/laboratory/DiscoverersList'
import type { ArtifactRead, Essence } from '../types'
import { useI18n } from '../hooks/useI18n'

/** Получает локализованное название */
function getLocalizedName(
  name: Record<string, string> | undefined,
  lang: string,
  fallback: string
): string {
  if (!name) return fallback
  return name[lang] || name.en || name.ru || fallback
}

const LaboratoryPage = () => {
  const { essences, artifacts: configArtifacts } = useConfigStore()
  const { player, updateBalance, language } = usePlayerStore()
  const { t } = useI18n()
  const { toasts, addToast, removeToast } = useToast()
  const [activeTab, setActiveTab] = useState('craft')
  const [selectedDomain, setSelectedDomain] = useState('')
  const [selectedEssences, setSelectedEssences] = useState<string[]>([])
  const [xgenAmount, setXgenAmount] = useState(100)
  const [isCrafting, setIsCrafting] = useState(false)
  const [craftResult, setCraftResult] = useState<{ status: string; hash: string } | null>(null)
  const [artifacts, setArtifacts] = useState<ArtifactRead[]>([])
  const [isLoadingArtifacts, setIsLoadingArtifacts] = useState(false)

  // Реальные эссенции из конфига с моковыми количествами (инвентарь пока в разработке)
  const essenceList = useMemo(() => {
    return Object.values(essences).map((essence: Essence) => ({
      slug: essence.slug,
      name: getLocalizedName(essence.name, language, essence.slug),
      tier: essence.tier,
      rarity: essence.rarity,
      domain: essence.domain,
      count: Math.floor(Math.random() * 15) + 1, // TODO: заменить на реальный инвентарь
    }))
  }, [essences, language])

  // Уникальные домены из эссенций
  const domainList = useMemo(() => {
    const domains = new Set<string>()
    Object.values(essences).forEach((essence: Essence) => {
      if (essence.domain) domains.add(essence.domain)
    })
    return Array.from(domains).sort()
  }, [essences])

  // Локализованные названия доменов
  const domainNames: Record<string, string> = useMemo(() => ({
    adhesive: language === 'ru' ? 'Клеящие' : language === 'la' ? 'Adhesiva' : 'Adhesive',
    probability: language === 'ru' ? 'Вероятность' : language === 'la' ? 'Probabilitas' : 'Probability',
    metallic: language === 'ru' ? 'Металлические' : language === 'la' ? 'Metallica' : 'Metallic',
    crystalline: language === 'ru' ? 'Кристаллические' : language === 'la' ? 'Crystallina' : 'Crystalline',
    energy: language === 'ru' ? 'Энергия' : language === 'la' ? 'Energia' : 'Energy',
    organic: language === 'ru' ? 'Органика' : language === 'la' ? 'Organica' : 'Organic',
    quantum: language === 'ru' ? 'Квантовые' : language === 'la' ? 'Quantica' : 'Quantum',
    optical: language === 'ru' ? 'Оптика' : language === 'la' ? 'Optica' : 'Optical',
    mechanical: language === 'ru' ? 'Механика' : language === 'la' ? 'Mechanica' : 'Mechanical',
    electronic: language === 'ru' ? 'Электроника' : language === 'la' ? 'Electronica' : 'Electronic',
    temporal: language === 'ru' ? 'Временные' : language === 'la' ? 'Temporale' : 'Temporal',
    cosmic: language === 'ru' ? 'Космические' : language === 'la' ? 'Cosmica' : 'Cosmic',
  }), [language])

  // Цвета редкости по тиру
  const RARITY_COLORS: Record<number, { border: string; text: string; bg: string }> = {
    1: { border: 'border-gray-500/30', text: 'text-gray-400', bg: 'bg-gray-500/10' },
    2: { border: 'border-green-500/30', text: 'text-green-400', bg: 'bg-green-500/10' },
    3: { border: 'border-blue-500/30', text: 'text-blue-400', bg: 'bg-blue-500/10' },
    4: { border: 'border-purple-500/30', text: 'text-purple-400', bg: 'bg-purple-500/10' },
    5: { border: 'border-yellow-500/30', text: 'text-yellow-400', bg: 'bg-yellow-500/10' },
  }

  const labTabs = [
    { id: 'craft', label: t('tab.craft') },
    { id: 'essences', label: t('tab.essences') },
    { id: 'staking', label: t('tab.staking') },
    { id: 'discoverers', label: t('tab.discoverers') },
  ]

  const handleEssenceToggle = useCallback((slug: string) => {
    setSelectedEssences((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug]
    )
  }, [])

  const handleCraft = async () => {
    if (!selectedDomain || selectedEssences.length < 3) {
      addToast(t('lab.toast.select'), 'error')
      return
    }

    setIsCrafting(true)
    try {
      const result = await craftArtifact(selectedDomain, selectedEssences, xgenAmount)
      setCraftResult({ status: result.status, hash: result.recipe_hash })
      updateBalance(-result.xgen_burned)

      if (result.status === 'created') {
        addToast(t('lab.toast.created'), 'success')
      } else {
        addToast(t('lab.toast.known'), 'info')
      }
    } catch (err) {
      console.error('Craft failed:', err)
      addToast(t('lab.toast.error'), 'error')
    } finally {
      setIsCrafting(false)
    }
  }

  const loadArtifacts = useCallback(async () => {
    setIsLoadingArtifacts(true)
    try {
      const data = await getArtifacts()
      setArtifacts(data)
    } catch (err) {
      console.warn('Failed to load artifacts, using mock data')
      setArtifacts([])
    } finally {
      setIsLoadingArtifacts(false)
    }
  }, [])

  const handleStake = async (artifactId: string) => {
    try {
      await stakeArtifact(artifactId)
      addToast(t('lab.toast.staked'), 'success')
      loadArtifacts()
    } catch (err) {
      addToast(t('lab.toast.stake.error'), 'error')
    }
  }

  const handleUnstake = async (artifactId: string) => {
    try {
      await unstakeArtifact(artifactId)
      addToast(t('lab.toast.unstaked'), 'success')
      loadArtifacts()
    } catch (err) {
      addToast(t('lab.toast.unstake.error'), 'error')
    }
  }

  const handleClaimYield = async (artifactId: string) => {
    try {
      const result = await claimYield(artifactId)
      updateBalance(Math.floor(result.claimed_amount))
      addToast(`${t('lab.toast.claimed')} ${result.claimed_amount.toFixed(2)} $XGEN`, 'success')
      loadArtifacts()
    } catch (err) {
      addToast(t('lab.toast.no.yield'), 'error')
    }
  }

  return (
    <div className="relative min-h-screen pt-28 pb-24 px-3">
      <Starfield />
      <ToastContainer toasts={toasts} removeToast={removeToast} />

      <div className="relative z-10 max-w-lg mx-auto">
        <WalletConnect />
        <SubMenu tabs={labTabs} activeTab={activeTab} onChange={setActiveTab} />

        <AnimatePresence mode="wait">
          {activeTab === 'craft' && (
            <motion.div
              key="craft"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="mt-4 space-y-4"
            >
              <div className="bg-white/5 backdrop-blur-xl border border-cosmic-border rounded-2xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <FlaskConical className="w-4 h-4 text-neon-cyan" />
                  <h3 className="text-sm font-bold text-white">{t('lab.domain')}</h3>
                </div>
                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
                  {domainList.map((domain) => (
                    <button
                      key={domain}
                      onClick={() => setSelectedDomain(domain)}
                      className={`flex-shrink-0 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                        selectedDomain === domain
                          ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50'
                          : 'bg-cosmic-card text-gray-400 border border-cosmic-border hover:border-gray-500'
                      }`}
                    >
                      {domainNames[domain] || domain}
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-white/5 backdrop-blur-xl border border-cosmic-border rounded-2xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Gem className="w-4 h-4 text-neon-purple" />
                    <h3 className="text-sm font-bold text-white">{t('lab.essences')}</h3>
                  </div>
                  <span className="text-xs text-gray-400">{selectedEssences.length}/5</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {essenceList.map((essence) => {
                    const isSelected = selectedEssences.includes(essence.slug)
                    const rarity = RARITY_COLORS[essence.tier] || RARITY_COLORS[1]
                    return (
                      <button
                        key={essence.slug}
                        onClick={() => essence.count > 0 && handleEssenceToggle(essence.slug)}
                        disabled={essence.count === 0}
                        className={`p-3 rounded-xl text-center text-xs font-medium transition-all disabled:opacity-30 disabled:cursor-not-allowed ${
                          isSelected
                            ? `${rarity.bg} ${rarity.text} border ${rarity.border} shadow-[0_0_8px_rgba(168,85,247,0.3)]`
                            : 'bg-cosmic-card text-gray-400 border border-cosmic-border hover:border-gray-500'
                        }`}
                      >
                        <span className="block text-lg mb-1">💎</span>
                        <span className="block">{essence.name}</span>
                        <span className="text-[10px] text-gray-500">×{essence.count}</span>
                      </button>
                    )
                  })}
                </div>
              </div>

              <div className="bg-white/5 backdrop-blur-xl border border-cosmic-border rounded-2xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">{t('lab.catalyst')}</span>
                  <span className="text-sm font-bold text-neon-cyan">{xgenAmount}</span>
                </div>
                <input
                  type="range"
                  min={10}
                  max={1000}
                  step={10}
                  value={xgenAmount}
                  onChange={(e) => setXgenAmount(Number(e.target.value))}
                  className="w-full accent-neon-cyan"
                />
                <div className="flex justify-between text-[10px] text-gray-500 mt-1">
                  <span>10</span>
                  <span>1000</span>
                </div>
              </div>

              <button
                onClick={handleCraft}
                disabled={isCrafting || !selectedDomain || selectedEssences.length < 3}
                className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-neon-cyan/20 to-neon-purple/20 border border-neon-cyan/50 text-white font-bold text-sm tracking-widest uppercase disabled:opacity-50 disabled:cursor-not-allowed hover:from-neon-cyan/30 hover:to-neon-purple/30 transition-all"
              >
                {isCrafting ? t('lab.synthesizing') : t('lab.synthesize')}
              </button>

              {craftResult && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`bg-white/5 backdrop-blur-xl border rounded-2xl p-4 ${
                    craftResult.status === 'created' ? 'border-neon-green/50' : 'border-yellow-500/50'
                  }`}
                >
                  <h4 className={`text-sm font-bold ${craftResult.status === 'created' ? 'text-neon-green' : 'text-yellow-400'}`}>
                    {craftResult.status === 'created' ? `✦ ${t('lab.created')}` : `⚠ ${t('lab.known')}`}
                  </h4>
                  <p className="text-[10px] text-gray-400 mt-1 font-mono">{t('lab.hash')}: {craftResult.hash.slice(0, 16)}...</p>
                </motion.div>
              )}
            </motion.div>
          )}

          {activeTab === 'essences' && (
            <motion.div
              key="essences"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="mt-4 space-y-2"
            >
              {essenceList.filter((e) => e.count > 0).map((essence) => {
                const rarity = RARITY_COLORS[essence.tier] || RARITY_COLORS[1]
                return (
                  <div
                    key={essence.slug}
                    className={`bg-white/5 backdrop-blur-xl border ${rarity.border} rounded-xl p-3 flex items-center gap-3`}
                  >
                    <div className={`w-10 h-10 rounded-lg ${rarity.bg} flex items-center justify-center text-lg`}>💎</div>
                    <div className="flex-1">
                      <h4 className="text-sm font-semibold text-white">{essence.name}</h4>
                      <p className="text-[10px] text-gray-400">{t('misc.tier')} {essence.tier}</p>
                    </div>
                    <span className={`text-sm font-bold ${rarity.text}`}>×{essence.count}</span>
                  </div>
                )
              })}
            </motion.div>
          )}

          {activeTab === 'staking' && (
            <motion.div
              key="staking"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="mt-4 space-y-3"
            >
              <div className="bg-white/5 backdrop-blur-xl border border-cosmic-border rounded-2xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-4 h-4 text-yellow-400" />
                  <h3 className="text-sm font-bold text-white">{t('lab.pool')}</h3>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">{t('lab.remaining')}</span>
                    <span className="text-neon-cyan font-mono">38.5M / 40M $XGEN</span>
                  </div>
                  <div className="h-2 bg-cosmic-bg rounded-full overflow-hidden">
                    <div className="h-full w-[96%] bg-gradient-to-r from-neon-cyan to-neon-purple rounded-full" />
                  </div>
                </div>
              </div>

              {isLoadingArtifacts ? (
                <div className="flex justify-center py-8 text-gray-400 text-sm">{t('lab.loading')}</div>
              ) : artifacts.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                  <span className="text-3xl mb-3">⚡</span>
                  <p className="text-sm">{t('lab.no.artifacts')}</p>
                  <p className="text-xs text-gray-500 mt-1">{t('lab.no.artifacts.hint')}</p>
                </div>
              ) : (
                artifacts.map((artifact) => (
                  <div
                    key={artifact.id}
                    className="bg-white/5 backdrop-blur-xl border border-cosmic-border rounded-xl p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-semibold text-white">{artifact.slug}</h4>
                      <span className={`text-[10px] uppercase px-2 py-0.5 rounded-full ${
                        artifact.status === 'active' ? 'bg-neon-green/20 text-neon-green' : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {artifact.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-400 mb-3">
                      <div>{t('lab.cycles')}: {artifact.cycles_remaining}</div>
                      <div>{t('lab.yield')}: {artifact.accumulated_yield.toFixed(2)} $XGEN</div>
                    </div>
                    <div className="flex gap-2">
                      {!artifact.staked_at ? (
                        <button
                          onClick={() => handleStake(artifact.id)}
                          className="flex-1 py-2 rounded-lg bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50 text-xs font-medium hover:bg-neon-cyan/30 transition-colors"
                        >
                          {t('lab.stake')}
                        </button>
                      ) : (
                        <>
                          <button
                            onClick={() => handleClaimYield(artifact.id)}
                            className="flex-1 py-2 rounded-lg bg-neon-green/20 text-neon-green border border-neon-green/50 text-xs font-medium hover:bg-neon-green/30 transition-colors"
                          >
                            {t('lab.claim')}
                          </button>
                          <button
                            onClick={() => handleUnstake(artifact.id)}
                            className="flex-1 py-2 rounded-lg bg-red-500/20 text-red-400 border border-red-500/50 text-xs font-medium hover:bg-red-500/30 transition-colors"
                          >
                            {t('lab.unstake')}
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))
              )}
            </motion.div>
          )}

          {activeTab === 'discoverers' && (
            <motion.div
              key="discoverers"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="mt-4"
            >
              <div className="flex items-center gap-2 mb-4">
                <Trophy className="w-5 h-5 text-rarity-legendary" />
                <h3 className="text-sm font-bold text-white">{t('lab.hall')}</h3>
              </div>
              <DiscoverersList
                artifacts={configArtifacts}
                essences={essences}
                currentPlayerUsername={player?.username}
                language={language}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default LaboratoryPage
