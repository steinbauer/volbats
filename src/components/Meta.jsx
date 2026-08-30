import { useEffect } from 'react'

/**
 * Nastaví title a popisek stránky.
 *
 * Při prerenderu (tools/prerender.js) se DOM nemění — hodnoty se předávají
 * přes kontext v entry-server.jsx a vkládají rovnou do vygenerovaného HTML,
 * aby je vyhledávače i náhledy odkazů viděly bez spouštění JS.
 */
export default function Meta({ title, popis }) {
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
