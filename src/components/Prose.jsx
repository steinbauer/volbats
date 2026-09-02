import { useNavigate } from 'react-router-dom'
import { prepisObrazky } from '../obrazky'

const ZAKLAD = import.meta.env.BASE_URL.replace(/\/$/, '')

/**
 * Doplní do interních odkazů kořen webu. Na GitHub Pages běží web
 * v /volbats/, takže odkaz zapsaný jako /program/ by mířil mimo.
 */
function prepisOdkazy(html) {
  if (!ZAKLAD) return html
  return html.replace(/href="\/(?!\/)/g, `href="${ZAKLAD}/`)
}

/**
 * Vykreslí HTML přenesené ze starého webu.
 *
 * Obsah pochází z našich dat, ne od návštěvníků, takže vložení přes
 * dangerouslySetInnerHTML je v pořádku. Cesty k obrázkům i odkazům se cestou
 * srovnají a kliknutí na interní odkaz obslouží router, aby se stránka
 * nenačítala celá znovu.
 */
export default function Prose({ html, className }) {
  const navigace = useNavigate()

  function naKliknuti(e) {
    const odkaz = e.target.closest('a')
    if (!odkaz || e.defaultPrevented || e.button !== 0) return
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return
    if (odkaz.target && odkaz.target !== '_self') return

    const cil = new URL(odkaz.href, window.location.href)
    if (cil.origin !== window.location.origin) return

    e.preventDefault()
    navigace(cil.pathname.slice(ZAKLAD.length) + cil.search + cil.hash)
  }

  return (
    <div
      className={className}
      onClick={naKliknuti}
      dangerouslySetInnerHTML={{ __html: prepisOdkazy(prepisObrazky(html)) }}
    />
  )
}
