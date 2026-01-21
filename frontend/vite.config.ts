import { defineConfig } from 'vite'
import preact from '@preact/preset-vite'
import tailwindcss from '@tailwindcss/vite'
import path from "path"

export default defineConfig({
  base: './',
  plugins: [preact(), tailwindcss()],
  resolve: {
    alias: {
      "react": "preact/compat",
      "react-dom": "preact/compat",
      "react/jsx-runtime": "preact/jsx-runtime",
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
