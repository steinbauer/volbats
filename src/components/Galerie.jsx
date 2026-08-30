import { Link } from 'react-router-dom'
import { obrazek } from '../obrazky'
import kandidati from '../data/kandidati.json'

/**
 * Pásek fotek kandidátů na úvodní stránce. Dřív byl součástí HTML přeneseného
 * z CMS, takže po výměně kandidátky ukazoval lidi z roku 2022. Teď se skládá
 * z dat, takže se mění zároveň s kandidátkou.
 */
export default function Galerie() {
  return (
    <div className="galerie">
      {kandidati.map((k) => (
        <Link to={`/kandidati/${k.slug}/`} key={k.cislo} title={k.jmeno}>
          <img src={obrazek(k.foto)} alt={k.jmeno} loading="lazy" />
        </Link>
      ))}
    </div>
  )
}
