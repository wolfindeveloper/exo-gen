/**
 * Провайдер всплывающих уведомлений (toast).
 *
 * Обёртка вокруг react-hot-toast с кастомным оформлением
 * в стиле EXO GENESIS (glassmorphism, neon-акценты).
 *
 * Использование:
 *   import { toast } from 'react-hot-toast'
 *   toast.success('Экспедиция запущена!')
 *   toast.error('Недостаточно топлива')
 *   toast.info('Корабль в ремонте')
 */

import { Toaster } from 'react-hot-toast'

/**
 * Компонент-обёртка для глобального тостера.
 * Размещается в корне приложения (App.tsx).
 */
export function ToastProvider(): JSX.Element {
  return (
    <Toaster
      position="top-center"
      reverseOrder={false}
      gutter={8}
      toastOptions={{
        duration: 5000,
        style: {
          background: 'rgba(26, 31, 46, 0.95)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          borderRadius: '12px',
          color: '#E2E8F0',
          fontSize: '14px',
          fontWeight: '500',
          padding: '12px 16px',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.4)',
          maxWidth: '380px',
        },
        success: {
          iconTheme: {
            primary: '#06B6D4',
            secondary: '#0B0F19',
          },
          style: {
            borderColor: 'rgba(6, 182, 212, 0.5)',
          },
        },
        error: {
          iconTheme: {
            primary: '#EF4444',
            secondary: '#0B0F19',
          },
          style: {
            borderColor: 'rgba(239, 68, 68, 0.5)',
          },
        },
        loading: {
          iconTheme: {
            primary: '#A855F7',
            secondary: '#0B0F19',
          },
        },
      }}
    />
  )
}
