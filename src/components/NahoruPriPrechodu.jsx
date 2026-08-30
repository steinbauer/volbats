import { useEffect } from 'react'
import { useLocation, useNavigationType } from 'react-router-dom'

/**
 * Po přechodu na jinou stránku odroluje nahoru.
 *
 * Prohlížeč si drží pozici z předchozí stránky, takže kliknutí na kandidáta
 * uprostřed kandidátky otevřelo medailonek někde v půlce textu. Tlačítko
 * zpět (POP) necháváme být — tam je návrat na původní místo správně.
 */
export default function NahoruPriPrechodu() {
  const { pathname } = useLocation()
  const druh = useNavigationType()

  useEffect(() => {
    if (druh === 'POP') return
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [pathname, druh])

  return null
}
