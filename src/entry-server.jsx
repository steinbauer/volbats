import { renderToString } from 'react-dom/server'
// V React Routeru 7 už samostatný podbalík /server není — StaticRouter je
// rovnou v react-router.
import { StaticRouter } from 'react-router'
import App from './App'
import { SberMeta } from './components/Meta'
import './styles/main.scss'

/**
 * Vykreslí jednu adresu. Volá se z tools/prerender.js.
 *
 * Vrací kromě HTML i titulek a popisek, které si stránka za běhu nastavila —
 * prerender je vloží do hlavičky, aby je vyhledávače a náhledy odkazů viděly
 * bez spouštění JS.
 */
export function render(cesta, zaklad) {
  const meta = {}
  const html = renderToString(
    <SberMeta.Provider value={meta}>
      <StaticRouter location={cesta} basename={zaklad}>
        <App />
      </StaticRouter>
    </SberMeta.Provider>,
  )
  return { html, meta }
}

export { vsechnyCesty, cestyBezIndexu } from './routes'
