import { StrictMode, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import WebApp from '@twa-dev/sdk'
import { TonConnectUIProvider, THEME } from '@tonconnect/ui-react'
import App from './App'
import { usePlayerStore } from './store/usePlayerStore'
import { useConfigStore } from './store/useConfigStore'
import './index.css'

const manifestUrl = import.meta.env.VITE_TON_MANIFEST_URL || 'https://proud-pillows-slide.loca.lt/tonconnect-manifest.json'
const network = import.meta.env.VITE_TON_NETWORK || 'testnet'

function AppInitializer() {
  const fetchPlayer = usePlayerStore((s) => s.fetchPlayer)
  const loadConfigs = useConfigStore((s) => s.loadConfigs)

  useEffect(() => {
    WebApp.ready()
    WebApp.expand()
    WebApp.enableClosingConfirmation()
    WebApp.setHeaderColor('#0B0F19')
    WebApp.setBackgroundColor('#0B0F19')

    fetchPlayer()
    loadConfigs()
  }, [fetchPlayer, loadConfigs])

  return null
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <TonConnectUIProvider
      manifestUrl={manifestUrl}
      uiPreferences={{ theme: THEME.DARK }}
      actionsConfiguration={{
        returnStrategy: 'none',
      }}
    >
      <App />
      <AppInitializer />
    </TonConnectUIProvider>
  </StrictMode>
)
