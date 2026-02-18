import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 9003,
    host: '0.0.0.0',
    // @ts-ignore
    allowedHosts: ['idp.securitycentric.net', 'sc-api-us-v2.securitycentric.net'],
  }
})
