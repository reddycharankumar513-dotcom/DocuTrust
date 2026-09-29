/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#060913",
        panel: "#0D1424",
        muted: "#8B98B7",
        border: "#1D2A44",
        primary: "#2563EB",
        success: "#14B8A6",
        warning: "#F59E0B",
        danger: "#EF4444"
      },
      borderRadius: {
        card: "8px"
      },
      boxShadow: {
        "panel": "0 20px 60px rgba(0, 0, 0, 0.38)"
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: []
};
