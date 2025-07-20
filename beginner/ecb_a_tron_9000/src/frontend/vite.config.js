import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "localhost",
    proxy: {
      "/encrypt": "http://localhost:8000",
      "/encrypt_batch": "http://localhost:8000",
    },
  },
  base: "/",
});
