/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./*.html'],
  theme: {
    screens: {
      sm:'480px',
      md:'768px',
      lg: '976px',
      xl: '1440px'
    },
    fontFamily:{
      'IBM' : ['IBM Plex Sans']
    },
    extend: {
      colors: {
        loginbutton: '#F6F0E8',
        freetrial: '#14203E'
      }
    },
  },
  plugins: [],
}

