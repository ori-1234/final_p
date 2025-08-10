import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Ethers.js polyfills
import { Buffer } from 'buffer'
import * as ethers from 'ethers'

// Set up globals that ethers.js requires
window.Buffer = Buffer
window.global = globalThis
window.process = { env: { } }
window.ethers = ethers

// Additional polyfills required by ethers
if (typeof window !== 'undefined') {
  window.process = {
    env: { },
    browser: true,
    version: '0.0.0',
    nextTick: (fn) => setTimeout(fn, 0)
  }
}

createRoot(document.getElementById('root')).render(
    <StrictMode>
      <App />
    </StrictMode>
)
