import { Link } from 'react-router-dom'
import { obrazek } from '../obrazky'
import { kandidati, odkazNaMedailonek } from '../data/lide'

const SIRKY = [400, 800]
// Osm miniatur na řádek v kontejneru do 1440 px, na užších méně sloupců
const SIZES = '(min-width: 1200px) 165px, (min-width: 992px) 11vw, (min-width: 768px) 15vw, (min-width: 576px) 22vw, 30vw'

/** Pásek fotek kandidátů na úvodní stránce. */
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
