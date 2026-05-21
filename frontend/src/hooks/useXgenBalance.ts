/**
 * Хук для получения баланса XGEN Jetton из подключённого кошелька.
 * Использует TON API (testnet/mainnet) для запроса jetton балансов.
 */

import { useState, useEffect } from 'react'
import { useTonAddress } from '@tonconnect/ui-react'

const TON_API_URL = import.meta.env.VITE_TON_NETWORK === 'testnet'
  ? 'https://testnet.tonapi.io'
  : 'https://tonapi.io'

/** Адрес XGEN Jetton Master (заполняется после деплоя контракта) */
const XGEN_JETTON_MASTER = import.meta.env.VITE_XGEN_JETTON_ADDRESS || ''

interface UseXgenBalanceResult {
  balance: number
  loading: boolean
  error: string | null
}

export function useXgenBalance(): UseXgenBalanceResult {
  const address = useTonAddress()
  const [balance, setBalance] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!address) {
      setBalance(0)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    const fetchBalance = async () => {
      try {
        // Если XGEN Jetton ещё не задеплоен — используем моковый баланс
        if (!XGEN_JETTON_MASTER) {
          if (!cancelled) {
            setBalance(1000) // Моковый баланс для dev
            setLoading(false)
          }
          return
        }

        const response = await fetch(
          `${TON_API_URL}/v2/accounts/${address}/jettons`,
          {
            headers: { 'Accept': 'application/json' },
          }
        )

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }

        const data = await response.json()
        const jettons = data.balances || []

        // Ищем XGEN Jetton по адресу master
        const xgenJetton = jettons.find(
          (j: any) => j.jetton.address === XGEN_JETTON_MASTER
        )

        if (xgenJetton) {
          // Баланс приходит в smallest units (обычно 9 decimals)
          const decimals = xgenJetton.jetton.decimals || 9
          const rawBalance = parseInt(xgenJetton.balance, 10)
          const humanBalance = rawBalance / Math.pow(10, decimals)

          if (!cancelled) {
            setBalance(humanBalance)
          }
        } else {
          if (!cancelled) {
            setBalance(0)
          }
        }
      } catch (err) {
        console.error('Failed to fetch XGEN balance:', err)
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unknown error')
          setBalance(1000) // Fallback на моковый баланс
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchBalance()

    return () => {
      cancelled = true
    }
  }, [address])

  return { balance, loading, error }
}
