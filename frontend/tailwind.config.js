/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        kolosal: {
          DEFAULT: '#0D0E0F',
          50: '#F5F5F6',
          100: '#E5E6E7',
          200: '#CBCCCF',
          300: '#A1A3A8',
          400: '#76797F',
          500: '#5B5E64',
          600: '#4D5055',
          700: '#424447',
          800: '#3A3C3E',
          900: '#333536',
          950: '#0D0E0F',
        },
        accent: {
          DEFAULT: '#6366F1',
          50: '#EDEFFD',
          100: '#DFE1FC',
          200: '#C2C5F9',
          300: '#A5A9F6',
          400: '#888DF3',
          500: '#6366F1',
          600: '#3136EC',
          700: '#1519C9',
          800: '#101396',
          900: '#0B0D64',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
