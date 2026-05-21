/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_TON_NETWORK: string
  readonly VITE_TON_MANIFEST_URL: string
  readonly VITE_WORLD_ID_APP_ID: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
