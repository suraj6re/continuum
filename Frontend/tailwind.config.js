/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          charcoal: '#1C1917',
          orange: '#EA580C',
          amber: '#D97706',
        },
        bg: {
          page: '#FAFAF9',
          card: '#FFFFFF',
          section: '#F5F5F4',
        },
        text: {
          primary: '#1C1917',
          secondary: '#57534E',
          muted: '#A8A29E',
        },
        border: {
          warm: '#E7E5E4',
        },
      },
    },
  },
  plugins: [],
}
