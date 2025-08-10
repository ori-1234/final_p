//const { html } = require("framer-motion/client");
/** @type {import('tailwindcss').Config} */

module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}", // Include all paths to your files
  ],
  theme: {
    extend: {
      screens: {
        xs: '370px', // Define a custom breakpoint for extra small screens
      },
      colors: {
        white: '#fff',
        black: '#111',
        blue: '#3a80e9', 
        grey: '#888',
        darkgrey: '#14171c',
        green: '#61c96f',
        red: '#f94141',
        lightblue: '#87CEEB',
        purple: 'rgb(165, 4, 165)',
      },
      boxShadow: {
        'custom-blue': '5px 5px 10px rgba(58, 128, 233, 0.5)',
      },
    },
  },
  plugins: [],
};
