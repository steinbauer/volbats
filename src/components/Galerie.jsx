import { Link } from 'react-router-dom'
import { obrazek } from '../obrazky'
import { kandidati, odkazNaMedailonek } from '../data/lide'

const SIRKY = [400, 800, 1200]
// Pět fotek na řádek v kontejneru do 1440 px, na užších displejích méně
const SIZES = '(min-width: 1200px) 260px, (min-width: 992px) 24vw, (min-width: 768px) 30vw, 45vw'

/** Fotky kandidátů na úvodní stránce — jediný blok s lidmi, co tam je. */
export default function Galerie() {
  return (
    <div className="galerie">
      {kandidati.map((k) => (
        <Link to={odkazNaMedailonek(k) ?? '/kandidati/'} key={k.cislo} title={k.jmeno}>
          <img
            src={obrazek(`${k.foto}-400.webp`)}
            srcSet={SIRKY.map((w) => `${obrazek(`${k.foto}-${w}.webp`)} ${w}w`).join(', ')}
            sizes={SIZES}
            alt={k.jmeno}
            loading="lazy"
          />
          <span className="kandidat__cislo kandidat__cislo--male">{k.cislo}</span>
        </Link>
      ))}
    </div>
  )
}
