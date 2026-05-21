import { useMemo } from 'react'
import { usePlayerStore } from '../store/usePlayerStore'
import { translations, TranslationKey, Language } from '../lib/i18n'

export function useI18n() {
  const language = usePlayerStore((s) => s.language)

  const t = useMemo(() => {
    return (key: TranslationKey): string => {
      const entry = translations[key]
      if (!entry) return key
      return (entry as Record<string, string>)[language] || entry.ru || key
    }
  }, [language])

  return { t, language }
}
