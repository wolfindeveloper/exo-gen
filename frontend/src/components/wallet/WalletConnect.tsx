/**
 * Компонент подключения TON-кошелька через TonConnect.
 * Показывает кнопку подключения или адрес подключённого кошелька.
 */

import { memo, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Wallet, Link2Off, AlertCircle } from 'lucide-react'
import { useTonAddress, useTonConnectUI, useTonWallet } from '@tonconnect/ui-react'

const WalletConnect = memo(() => {
  const [tonConnectUI] = useTonConnectUI()
  const wallet = useTonWallet()
  const address = useTonAddress()
  const [error, setError] = useState<string | null>(null)

  const handleConnect = useCallback(async () => {
    setError(null)
    try {
      await tonConnectUI.openModal()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      if (message.includes('declined') || message.includes('rejected')) {
        setError('Подключение отклонено. Попробуйте снова.')
      } else if (message.includes('manifest')) {
        setError('Manifest недоступен. Запустите сервер и проверьте URL.')
      } else {
        setError(`Ошибка: ${message.slice(0, 60)}`)
      }
    }
  }, [tonConnectUI])

  const handleDisconnect = useCallback(() => {
    tonConnectUI.disconnect()
    setError(null)
  }, [tonConnectUI])

  if (!address || !wallet) {
    return (
      <div className="w-full space-y-2">
        <motion.button
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          onClick={handleConnect}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-cosmic-border hover:border-neon-cyan/50 text-gray-300 hover:text-neon-cyan text-xs font-medium transition-all"
        >
          <Wallet className="w-3.5 h-3.5" />
          Подключить Tonkeeper
        </motion.button>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="flex items-center gap-2 px-3 py-2 rounded-xl bg-red-500/10 border border-red-500/20"
            >
              <AlertCircle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
              <p className="text-[10px] text-red-400">{error}</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  }

  const shortAddress = `${address.slice(0, 6)}...${address.slice(-4)}`
  const chain = wallet.account?.chain === '-2' ? 'testnet' : 'mainnet'

  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full flex items-center justify-between gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-neon-cyan/30"
    >
      <div className="flex items-center gap-2">
        <div className="w-5 h-5 rounded-full bg-neon-cyan/20 flex items-center justify-center">
          <Wallet className="w-3 h-3 text-neon-cyan" />
        </div>
        <div className="flex flex-col">
          <span className="text-xs font-mono text-neon-cyan">{shortAddress}</span>
          <span className="text-[9px] text-gray-500">{chain}</span>
        </div>
      </div>
      <button
        onClick={handleDisconnect}
        className="flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-red-500/10 text-gray-500 hover:text-red-400 text-[10px] font-medium transition-all"
      >
        <Link2Off className="w-3 h-3" />
        Отключить
      </button>
    </motion.div>
  )
})

WalletConnect.displayName = 'WalletConnect'
export default WalletConnect
