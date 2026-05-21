import { memo, useState, useEffect } from 'react'
import { Volume2, VolumeX, Wallet } from 'lucide-react'
import { useTonAddress, useTonConnectUI } from '@tonconnect/ui-react'
import { isMuted, toggleMute } from '../../lib/sounds'
import { usePlayerStore } from '../../store/usePlayerStore'
import { useI18n } from '../../hooks/useI18n'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

const SettingsModal = memo(({ isOpen, onClose }: SettingsModalProps) => {
  const [soundEnabled, setSoundEnabled] = useState(!isMuted())
  const [musicEnabled, setMusicEnabled] = useState(false)
  const [nickname, setNickname] = useState('')
  const { language, setLanguage } = usePlayerStore()
  const { t } = useI18n()
  const [tonConnectUI] = useTonConnectUI()
  const address = useTonAddress()

  const languages = [
    { code: 'ru' as const, label: t('lang.ru') },
    { code: 'en' as const, label: t('lang.en') },
    { code: 'la' as const, label: t('lang.la') },
  ]

  useEffect(() => {
    if (isOpen) {
      setSoundEnabled(!isMuted())
    }
  }, [isOpen])

  if (!isOpen) return null

  const handleSoundToggle = () => {
    const newMuted = toggleMute()
    setSoundEnabled(!newMuted)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold text-white">{t('settings.title')}</h2>
          <button
            onClick={onClose}
            className="min-w-[44px] min-h-[44px] flex items-center justify-center text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6">
          {/* Язык */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">{t('settings.language')}</label>
            <div className="flex gap-2">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                    lang.code === language
                      ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/50'
                      : 'bg-cosmic-bg text-gray-400 border border-cosmic-border hover:border-gray-500'
                  }`}
                >
                  {lang.label}
                </button>
              ))}
            </div>
          </div>

          {/* Никнейм */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">{t('settings.nickname')}</label>
            <input
              type="text"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              className="input-field w-full"
              placeholder={t('settings.nickname.placeholder')}
              maxLength={32}
            />
          </div>

          {/* Аватар */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">{t('settings.avatar')}</label>
            <div className="flex gap-2">
              {['default', 'pilot', 'captain'].map((avatar) => (
                <button
                  key={avatar}
                  className="w-12 h-12 rounded-full bg-cosmic-bg border-2 border-cosmic-border hover:border-neon-cyan transition-colors"
                >
                  <span className="text-lg">{avatar === 'default' ? '👤' : avatar === 'pilot' ? '🧑‍🚀' : '👨‍✈️'}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Звуки */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {soundEnabled ? (
                <Volume2 className="w-4 h-4 text-neon-cyan" />
              ) : (
                <VolumeX className="w-4 h-4 text-gray-500" />
              )}
              <span className="text-sm font-medium text-gray-300">{t('settings.sound')}</span>
            </div>
            <button
              onClick={handleSoundToggle}
              className={`w-12 h-6 rounded-full transition-colors ${
                soundEnabled ? 'bg-neon-cyan' : 'bg-cosmic-border'
              }`}
              aria-label={soundEnabled ? t('settings.sound.on') : t('settings.sound.off')}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform ${
                  soundEnabled ? 'translate-x-6' : 'translate-x-0.5'
                }`}
              />
            </button>
          </div>

          {/* Фоновая музыка */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-300">{t('settings.music')}</span>
            <button
              onClick={() => setMusicEnabled(!musicEnabled)}
              className={`w-12 h-6 rounded-full transition-colors ${
                musicEnabled ? 'bg-neon-purple' : 'bg-cosmic-border'
              }`}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform ${
                  musicEnabled ? 'translate-x-6' : 'translate-x-0.5'
                }`}
              />
            </button>
          </div>

          {/* TON Wallet */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">{t('settings.wallet')}</label>
            {address ? (
              <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-white/5 border border-neon-cyan/30">
                <div className="flex items-center gap-2">
                  <Wallet className="w-4 h-4 text-neon-cyan" />
                  <span className="text-xs font-mono text-neon-cyan">
                    {address.slice(0, 6)}...{address.slice(-4)}
                  </span>
                </div>
                <button
                  onClick={() => tonConnectUI.disconnect()}
                  className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 text-xs font-medium hover:bg-red-500/20 transition-colors"
                >
                  Отключить
                </button>
              </div>
            ) : (
              <button
                onClick={() => tonConnectUI.openModal()}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <Wallet className="w-4 h-4" />
                {t('settings.wallet')}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
})

SettingsModal.displayName = 'SettingsModal'
export default SettingsModal
