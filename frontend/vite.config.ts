import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import process from "node:process";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // When running inside docker, frontend should proxy to the backend container
      // named 'backend'. When running locally (not in container) keep localhost.
      "/api": process.env.DOCKER ? "http://backend:8000/" : "http://localhost:8000/",
    },
  },
});
