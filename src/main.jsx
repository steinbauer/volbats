import { StrictMode } from 'react'
import { hydrateRoot, createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './styles/main.scss'

const zaklad = import.meta.env.BASE_URL.replace(/\/$/, '')
const korenovy = document.getElementById('root')

const strom = (
  <StrictMode>
    <BrowserRouter basename={zaklad}>
      <App />
    </BrowserRouter>
  </StrictMode>
)

// Stránky jsou předgenerované, takže se na hotové HTML jen napojíme.
// createRoot je záchranná varianta pro případ, že by HTML bylo prázdné.
if (korenovy.hasChildNodes()) {
  hydrateRoot(korenovy, strom)
} else {
  createRoot(korenovy).render(strom)
}
