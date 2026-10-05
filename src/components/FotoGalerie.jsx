import { useCallback, useEffect, useRef, useState } from 'react'
import { obrazek } from '../obrazky'

const MINIATURY = [400, 800]
const VELKA = 1400
// Tři miniatury na řádek ve sloupci s textem, na mobilu dvě
const SIZES = '(min-width: 1200px) 230px, (min-width: 768px) 20vw, 45vw'

/**
 * Fotky u medailonku: miniatury pod textem, po kliknutí přes celou obrazovku.
 *
 * Bývají to dvojice před a po pod sebou, takže miniatura ukazuje fotku celou
 * a nic z ní neořezává. Velká verze se stahuje až po otevření.
 */
export default function FotoGalerie({ fotky, nazev }) {
  const [otevrene, setOtevrene] = useState(null)
  const prepni = useCallback(
    (smer) => setOtevrene((i) => (i + smer + fotky.length) % fotky.length),
    [fotky.length],
  )

  return (
    <section className="fotogalerie" aria-label={nazev}>
      <h2 className="fotogalerie__nadpis">{nazev}</h2>
      <div className="fotogalerie__mrizka">
        {fotky.map((f, i) => (
          <button
            type="button"
            key={f.foto}
            onClick={() => setOtevrene(i)}
            aria-label={`Zvětšit: ${f.popis}`}
          >
            <img
              src={obrazek(`${f.foto}-400.webp`)}
              srcSet={MINIATURY.map((w) => `${obrazek(`${f.foto}-${w}.webp`)} ${w}w`).join(', ')}
              sizes={SIZES}
              alt={f.popis}
              loading="lazy"
            />
            <span className="fotogalerie__popis">{f.popis}</span>
          </button>
        ))}
      </div>

      <FotoLightbox
        fotky={fotky}
        otevrene={otevrene}
        zavri={() => setOtevrene(null)}
        prepni={prepni}
      />
    </section>
  )
}

/** Fotka přes celou obrazovku; stejný `<dialog>` a vzhled jako u videí. */
function FotoLightbox({ fotky, otevrene, zavri, prepni }) {
  const dialog = useRef(null)
  const aktivni = otevrene == null ? null : fotky[otevrene]

  useEffect(() => {
    const d = dialog.current
    if (!d) return
    if (aktivni && !d.open) d.showModal()
    if (!aktivni && d.open) d.close()
  }, [aktivni])

  useEffect(() => {
    if (!aktivni) return
    const posun = (e) => {
      if (e.key === 'ArrowRight') prepni(1)
      if (e.key === 'ArrowLeft') prepni(-1)
    }
    document.addEventListener('keydown', posun)
    return () => document.removeEventListener('keydown', posun)
  }, [aktivni, prepni])

  return (
    <dialog
      ref={dialog}
      className="lightbox"
      onClose={zavri}
      onClick={(e) => { if (e.target === dialog.current) zavri() }}
      aria-label={aktivni ? aktivni.popis : undefined}
    >
      {aktivni && (
        <div className="lightbox__telo">
          <p className="lightbox__nazev">{aktivni.popis}</p>

          <img
            className="lightbox__foto"
            key={aktivni.foto}
            src={obrazek(`${aktivni.foto}-${VELKA}.webp`)}
            alt={aktivni.popis}
          />

          <div className="lightbox__ovladani">
            <button type="button" onClick={() => prepni(-1)} aria-label="Předchozí fotka">
              ‹
            </button>
            <span>
              {otevrene + 1} / {fotky.length}
            </span>
            <button type="button" onClick={() => prepni(1)} aria-label="Další fotka">
              ›
            </button>
          </div>

          <button
            type="button"
            className="lightbox__zavrit"
            onClick={zavri}
            aria-label="Zavřít"
          >
            ×
          </button>
        </div>
      )}
    </dialog>
  )
}
