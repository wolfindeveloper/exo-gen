/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cosmic: {
          bg: '#0B0F19',
          card: '#1A1F2E',
          cardHover: '#222838',
          border: '#2A3040',
        },
        neon: {
          cyan: '#06B6D4',
          purple: '#A855F7',
          pink: '#EC4899',
          green: '#22C55E',
        },
        rarity: {
          common: '#9CA3AF',
          uncommon: '#22C55E',
          rare: '#3B82F6',
          epic: '#A855F7',
          legendary: '#F59E0B',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-cyan': '0 0 10px rgba(6, 182, 212, 0.5), 0 0 20px rgba(6, 182, 212, 0.2)',
        'glow-purple': '0 0 10px rgba(168, 85, 247, 0.5), 0 0 20px rgba(168, 85, 247, 0.2)',
        'glow-common': '0 0 8px rgba(156, 163, 175, 0.3)',
        'glow-uncommon': '0 0 8px rgba(34, 197, 94, 0.3)',
        'glow-rare': '0 0 8px rgba(59, 130, 246, 0.4)',
        'glow-epic': '0 0 10px rgba(168, 85, 247, 0.5)',
        'glow-legendary': '0 0 12px rgba(245, 158, 11, 0.6)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(6, 182, 212, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(6, 182, 212, 0.6)' },
        },
      },
    },
  },
  plugins: [],
}
