import { prepisObrazky } from '../obrazky'

/**
 * Vykreslí HTML přenesené ze starého webu.
 *
 * Obsah pochází z našich dat (tools/extract.py ho vytáhl z kopie volbats.cz),
 * ne od návštěvníků, takže vložení přes dangerouslySetInnerHTML je v pořádku.
 * Cesty k obrázkům se cestou přepíšou na hashované URL od Vite.
 */
export default function Prose({ html, className }) {
  return (
    <div className={className} dangerouslySetInnerHTML={{ __html: prepisObrazky(html) }} />
  )
}
