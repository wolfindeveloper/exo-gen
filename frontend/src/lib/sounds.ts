/**
 * Менеджер звуковых эффектов через HTML5 Audio.
 *
 * Управляет воспроизведением, громкостью и состоянием mute.
 * Состояние mute сохраняется в localStorage.
 *
 * Использование:
 *   import { playSound, toggleMute, isMuted } from '@/lib/sounds'
 *   playSound('click')
 */

type SoundName = 'click' | 'expedition' | 'success' | 'error' | 'levelup'

interface SoundConfig {
  /** Путь к аудиофайлу относительно public/ */
  src: string
  /** Громкость по умолчанию (0–1) */
  volume: number
}

/** Конфигурация звуков — легко заменить на свои файлы */
const SOUND_CONFIGS: Record<SoundName, SoundConfig> = {
  click: { src: '/sounds/click.mp3', volume: 0.3 },
  expedition: { src: '/sounds/expedition.mp3', volume: 0.5 },
  success: { src: '/sounds/success.mp3', volume: 0.4 },
  error: { src: '/sounds/error.mp3', volume: 0.4 },
  levelup: { src: '/sounds/levelup.mp3', volume: 0.5 },
}

const MUTE_KEY = 'exo-genesis-sound-muted'

/** Singleton-менеджер звуков */
class SoundManager {
  private muted: boolean
  private audioCache: Map<string, HTMLAudioElement>

  constructor() {
    const stored = localStorage.getItem(MUTE_KEY)
    this.muted = stored === 'true'
    this.audioCache = new Map()
  }

  /** Проверить, включён ли звук */
  isMuted(): boolean {
    return this.muted
  }

  /** Переключить состояние mute и сохранить в localStorage */
  toggleMute(): boolean {
    this.muted = !this.muted
    localStorage.setItem(MUTE_KEY, String(this.muted))
    return this.muted
  }

  /** Установить состояние mute напрямую */
  setMute(value: boolean): void {
    this.muted = value
    localStorage.setItem(MUTE_KEY, String(this.muted))
  }

  /**
   * Воспроизвести звуковой эффект.
   * Если звук замьючен — ничего не делает.
   * При повторном вызове того же звука — перематывает в начало.
   */
  play(name: SoundName): void {
    if (this.muted) return

    const config = SOUND_CONFIGS[name]
    if (!config) {
      console.warn(`[SoundManager] Звук "${name}" не найден в конфиге`)
      return
    }

    let audio = this.audioCache.get(name)

    if (!audio) {
      audio = new Audio(config.src)
      audio.volume = config.volume
      audio.preload = 'auto'
      this.audioCache.set(name, audio)
    }

    // Перематываем в начало для повторного воспроизведения
    audio.currentTime = 0
    audio.play().catch(() => {
      // Игнорируем ошибки autoplay (браузер может блокировать)
    })
  }

  /** Предзагрузить все звуки (вызывать при старте приложения) */
  preloadAll(): void {
    for (const name of Object.keys(SOUND_CONFIGS) as SoundName[]) {
      const config = SOUND_CONFIGS[name]
      const audio = new Audio()
      audio.preload = 'auto'
      audio.src = config.src
      audio.volume = 0 // Не воспроизводим, только загружаем
      this.audioCache.set(name, audio)
    }
  }
}

/** Единственный экземпляр менеджера */
export const soundManager = new SoundManager()

/** Удобные обёртки для прямого вызова */
export const playSound = (name: SoundName): void => soundManager.play(name)
export const toggleMute = (): boolean => soundManager.toggleMute()
export const isMuted = (): boolean => soundManager.isMuted()
export const setMute = (value: boolean): void => soundManager.setMute(value)
