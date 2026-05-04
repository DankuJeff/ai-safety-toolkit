/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4ff',
          500: '#3b5bdb',
          600: '#3451c7',
          700: '#2c45b0',
          900: '#1a2a6e',
        },
        pass: '#22c55e',
        fail: '#ef4444',
        warn: '#f59e0b',
      },
    },
  },
  plugins: [],
}
