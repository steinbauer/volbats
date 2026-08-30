import { Link } from 'react-router-dom'
import { obrazek } from '../obrazky'
import kandidati from '../data/kandidati.json'

/**
 * Pásek fotek kandidátů na úvodní stránce. Skládá se z dat, takže se mění
 * zároveň s kandidátkou.
 */
export default function Galerie() {
  return (
    <div className="galerie">
      {kandidati.map((k) => (
        <Link to={`/kandidati/${k.slug}/`} key={k.cislo} title={k.jmeno}>
          <img src={obrazek(k.foto)} alt={k.jmeno} loading="lazy" />
          <span className="kandidat__cislo kandidat__cislo--male">{k.cislo}</span>
        </Link>
      ))}
    </div>
  )
}
