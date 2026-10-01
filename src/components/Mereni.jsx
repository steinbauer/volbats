import { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'

// Návštěvnost měříme sami na stats.volbats.cz (repo soukrome/stats.volbats.cz
// na git.polyweb.cz), nic nejde cizí službě. Bez cookies a bez čehokoli
// uloženého v prohlížeči, takže web nepotřebuje lištu se souhlasem.
const SBER = 'https://stats.volbats.cz/h'

// Lab, localhost i předgenerování mají čísla nechat být.
const OSTRY = /^(www\.)?volbats\.cz$/

export default function Mereni() {
  const { pathname } = useLocation()
  const predchozi = useRef(null)

  useEffect(() => {
    if (!OSTRY.test(window.location.hostname) || !navigator.sendBeacon) return
    // Při prvním zobrazení je odkud skutečný příchod (referrer, utm, fbclid).
    // Další stránky už jsou prokliky po webu — React Router přitom referrer
    // nemění, takže by se jinak každý proklik tvářil jako nový příchod
    // z Facebooku.
    const prvni = predchozi.current === null
    navigator.sendBeacon(SBER, JSON.stringify({
      p: pathname,
      r: prvni ? document.referrer : predchozi.current,
      s: prvni ? window.location.search : '',
    }))
    predchozi.current = window.location.href
  }, [pathname])

  return null
}
