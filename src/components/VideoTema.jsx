import { useEffect, useRef } from 'react'
import videaData from '../data/videa.json'

export const videa = videaData.videa
export const videaPodleSekce = Object.fromEntries(
  videa.map((v, poradi) => [v.sekce, { ...v, poradi }]),
)

/**
 * Náhled videa u sekce programu.
 *
 * Dokud na něj nikdo neklikne, je to obrázek a tlačítko — prohlížeč nestahuje
 * nic z videa a stránka se načítá stejně rychle jako dřív. Náhled je první
 * kreslený záběr, takže po spuštění obraz nepřeskočí.
 */
export default function VideoTema({ video, otevri }) {
  return (
    <div className="tema-video">
      <button
        type="button"
        className="tema-video__nahled"
        onClick={() => otevri(video.poradi)}
        aria-label={`Přehrát video: ${video.nazev}`}
      >
        <img src={`/videa/${video.soubor}.jpg`} alt="" loading="lazy" />
        <span className="tema-video__tlacitko" aria-hidden="true">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="48" />
            <path d="M40 30 L72 50 L40 70 Z" />
          </svg>
        </span>
        <span className="tema-video__popis">
          Video <b>{video.delka}</b>
        </span>
      </button>
    </div>
  )
}

/**
 * Přehrávač přes celou obrazovku, ve kterém se mezi videi listuje.
 *
 * Stojí na `<dialog>`, takže zavírání Escapem, překryv pod obsahem i vrácení
 * ohniska na tlačítko, ze kterého se otevřelo, obstará prohlížeč sám.
 * Přehrává se právě jedno video: při listování se předchozí odpojí, tak
 * nemají jak mluvit přes sebe.
 */
export function VideoLightbox({ otevrene, zavri, prepni }) {
  const dialog = useRef(null)
  const video = useRef(null)
  const aktivni = otevrene == null ? null : videa[otevrene]

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
      // Kliknutí vedle videa zavírá; uvnitř se musí zastavit, ať nezavře
      // i klik na ovládací prvky přehrávače.
      onClick={(e) => { if (e.target === dialog.current) zavri() }}
      aria-label={aktivni ? `Video: ${aktivni.nazev}` : undefined}
    >
      {aktivni && (
        <div className="lightbox__telo">
          <p className="lightbox__nazev">{aktivni.nazev}</p>

          <video
            ref={video}
            key={aktivni.soubor}
            controls
            autoPlay
            playsInline
            poster={`/videa/${aktivni.soubor}.jpg`}
            src={`/videa/${aktivni.soubor}.mp4`}
          />

          <div className="lightbox__ovladani">
            <button type="button" onClick={() => prepni(-1)} aria-label="Předchozí video">
              ‹
            </button>
            <span>
              {otevrene + 1} / {videa.length}
            </span>
            <button type="button" onClick={() => prepni(1)} aria-label="Další video">
              ›
            </button>
          </div>

          <p className="lightbox__dalsi">
            Další: {videa[(otevrene + 1) % videa.length].nazev}
          </p>

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
