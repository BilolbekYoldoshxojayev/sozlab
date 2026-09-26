/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        vazir: {
          blue: "#0B2B50",
          navy: "#081E38",
          sky: "#1E6091",
          gold: "#D4AF37",
          emerald: "#0E7490",
          teal: "#0D9488",
          light: "#F8FAFC",
          card: "#FFFFFF",
          border: "#E2E8F0"
        },
        sozlab: {
          teal: "#035B60",
          tealHover: "#024B4F",
          tealDark: "#02373A",
          tealDarker: "#012022",
          tealBg: "#04181A",
          tealSurface: "#07262A",
          tealCard: "#092E33",
          tealBorder: "#0D4349",
          tealLight: "#0A7C83",
          orange: "#FC6F01",
          orangeHover: "#E56300",
          orangeLight: "#FFF4EB",
          orangeBorder: "#FD8C33",
          orangeDark: "#BF5300",
        }
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"]
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "wave": "wave 1.5s ease-in-out infinite",
        "fade-in": "fadeIn 0.3s ease-out forwards",
      },
      keyframes: {
        wave: {
          "0%, 100%": { transform: "scaleY(0.4)" },
          "50%": { transform: "scaleY(1.0)" },
        },
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        }
      }
    },
  },
  plugins: [],
}
