import { useEffect } from 'react'
import { useLocation, useNavigationType } from 'react-router-dom'

/**
 * Po přechodu na jinou stránku odroluje nahoru.
 *
 * Prohlížeč si drží pozici z předchozí stránky, takže kliknutí na kandidáta
 * uprostřed kandidátky otevřelo medailonek někde v půlce textu. Tlačítko
 * zpět (POP) necháváme být — tam je návrat na původní místo správně.
 *
 * Odkaz s kotvou (dlaždice na úvodní stránce míří na /program/#sport) je
 * výjimka: prohlížeč si sám kotvu nenajde, protože cílová stránka v tu chvíli
 * ještě není vykreslená. Doroluje se tedy na ni ručně, a když taková kotva
 * na stránce není, zůstává původní chování — nahoru.
 */
export default function NahoruPriPrechodu() {
  const { pathname, hash } = useLocation()
  const druh = useNavigationType()

  useEffect(() => {
    if (druh === 'POP') return

    if (hash) {
      const cil = document.getElementById(decodeURIComponent(hash.slice(1)))
      if (cil) {
        cil.scrollIntoView()
        return
      }
    }

    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [pathname, hash, druh])

  return null
}
