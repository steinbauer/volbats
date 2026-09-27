import { useEffect, useRef } from 'react'
import videaData from '../data/videa.json'

export const videaPodleSekce = Object.fromEntries(
  videaData.videa.map((v, poradi) => [v.sekce, { ...v, poradi }]),
)
export const videa = videaData.videa

/**
 * Video k jedné sekci programu.
 *
 * Dokud na něj nikdo neklikne, je to obrázek a tlačítko — prohlížeč nestahuje
 * nic z videa a stránka se načítá stejně rychle jako dřív. Náhled je první
 * kreslený záběr, takže po spuštění obraz nepřeskočí.
 *
 * Které video hraje, drží stránka, ne komponenta: jinak by šlo spustit dvě
 * naráz a mluvily by přes sebe.
 */
export default function VideoTema({ video, hraje, spust, dalsi }) {
  const prvek = useRef(null)

  useEffect(() => {
    if (hraje) prvek.current?.play().catch(() => {})
  }, [hraje])

  if (!hraje) {
    return (
      <div className="tema-video">
        <button
          type="button"
          className="tema-video__nahled"
          onClick={() => spust(video.sekce)}
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

  return (
    <div className="tema-video tema-video--hraje">
      {/* controls i po spuštění: divák musí mít čím zastavit a přetočit */}
      <video
        ref={prvek}
        controls
        playsInline
        preload="auto"
        poster={`/videa/${video.soubor}.jpg`}
        src={`/videa/${video.soubor}.mp4`}
      />
      {dalsi && (
        <button type="button" className="tema-video__dalsi" onClick={() => spust(dalsi.sekce)}>
          Další video: {dalsi.nazev} →
        </button>
      )}
    </div>
  )
}
