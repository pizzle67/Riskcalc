/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  safelist: [
    "text-input-pink",
    "text-input-blue",
    "bg-input-pink",
    "bg-input-blue",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#000000",
        canvas: "#ffffff",
        "input-blue": "#1d4ed8",
        "input-blue-soft": "#3b82f6",
        "input-pink": "#db2777",
        "input-pink-soft": "#ec4899",
        "dial-grey": "#9ca3af",
        "button-grey": "#e5e7eb",
        "panel-grey": "#f3f4f6",
        "line-grey": "#d1d5db",
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
