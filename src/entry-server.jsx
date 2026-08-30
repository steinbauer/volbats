import { renderToString } from 'react-dom/server'
// V React Routeru 7 už samostatný podbalík /server není — StaticRouter je
// rovnou v react-router.
import { StaticRouter } from 'react-router'
import App from './App'
import './styles/main.scss'

/** Vykreslí jednu adresu do HTML. Volá se z tools/prerender.js. */
export function render(cesta, zaklad) {
  return renderToString(
    <StaticRouter location={cesta} basename={zaklad}>
      <App />
    </StaticRouter>,
  )
}

export { vsechnyCesty } from './routes'
