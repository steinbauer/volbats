import { createContext, useContext, useEffect } from 'react'

/**
 * Sběrač titulku a popisku pro předgenerování.
 *
 * V prohlížeči kontext nikdo neposkytuje, zůstane `null` a hodnoty se
 * nastaví přes `useEffect` níž. Při předgenerování ho dodá entry-server.jsx
 * a prerender si z něj hodnoty vyzvedne — `useEffect` se na serveru
 * nespustí, takže jinak by v HTML zůstal jen výchozí titulek ze šablony
 * a robot by na všech stránkách viděl tentýž.
 */
export const SberMeta = createContext(null)

/** Nastaví title a popisek stránky. */
export default function Meta({ title, popis }) {
  const sber = useContext(SberMeta)

  // Zápis během renderu je tu schválně: prerender potřebuje hodnoty hned,
  // jak se komponenta vykreslí, a `sber` je jeho vlastní objekt pro jedinou
  // právě vykreslovanou stránku — nic sdíleného mezi rendery.
  if (sber) {
    if (title) sber.title = title
    if (popis) sber.popis = popis
  }

  useEffect(() => {
    if (title) document.title = title
    if (popis) {
      let tag = document.querySelector('meta[name="description"]')
      if (!tag) {
        tag = document.createElement('meta')
        tag.setAttribute('name', 'description')
        document.head.appendChild(tag)
      }
      tag.setAttribute('content', popis)
    }
  }, [title, popis])

  return null
}
