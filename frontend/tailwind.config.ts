import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      // ─── GHARMIND AI Color System ─────────────────────────────────
      colors: {
        // Base (OS dark theme)
        background: {
          primary:   '#0F0F0F',
          secondary: '#1A1A2E',
          card:      '#16213E',
        },
        // Sidebar
        sidebar: '#0A0A1A',

        // Accent - Saffron (Indian identity)
        saffron: {
          50:  '#FFF5EE',
          100: '#FFE4CC',
          200: '#FFC899',
          300: '#FFB066',
          400: '#FF9033',
          500: '#FF6B35',  // Primary accent
          600: '#E55A20',
          700: '#CC4910',
          800: '#B23800',
          900: '#8F2C00',
        },

        // Accent - Gold (Festival mode)
        gold: {
          300: '#FFD966',
          400: '#FFC93D',
          500: '#FFB347',  // Festival accent
          600: '#E09830',
        },

        // Success / Good
        teal: {
          400: '#2DD4BF',
          500: '#00D4AA',
        },

        // Warning / Attention
        amber: {
          400: '#FBBF24',
          500: '#FFC107',
        },

        // Critical / Alert
        alert: {
          DEFAULT: '#EF4444',
          subtle:  '#7F1D1D',
        },

        // Text
        content: {
          primary:   '#F5F5F5',
          secondary: '#A0A0B0',
          muted:     '#606070',
        },
      },

      // ─── Font Families ────────────────────────────────────────────
      fontFamily: {
        sans:  ['Inter', 'Noto Sans Devanagari', 'sans-serif'],
        mono:  ['JetBrains Mono', 'monospace'],
        hindi: ['Noto Sans Devanagari', 'sans-serif'],
      },

      // ─── Animations ───────────────────────────────────────────────
      keyframes: {
        // Household "breathing" animation
        breathe: {
          '0%, 100%': { transform: 'scale(1)', opacity: '1' },
          '50%':       { transform: 'scale(1.03)', opacity: '0.95' },
        },
        // Prediction card entry
        slideInTop: {
          '0%':   { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        // Festival glow pulse
        festivalGlow: {
          '0%, 100%': { boxShadow: '0 0 10px #FFB347' },
          '50%':       { boxShadow: '0 0 25px #FFB347, 0 0 50px #FF6B35' },
        },
        // Critical alert pulse
        criticalPulse: {
          '0%, 100%': { boxShadow: '0 0 5px #EF4444' },
          '50%':       { boxShadow: '0 0 20px #EF4444' },
        },
      },
      animation: {
        breathe:      'breathe 4s ease-in-out infinite',
        slideInTop:   'slideInTop 0.15s ease-out',
        festivalGlow: 'festivalGlow 2s ease-in-out infinite',
        criticalPulse:'criticalPulse 1s ease-in-out infinite',
      },

      // ─── Border Radius ────────────────────────────────────────────
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },

      // ─── Backdrop Blur ────────────────────────────────────────────
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
  ],
}

export default config
