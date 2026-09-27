import { Link } from 'react-router-dom'
import KandidatFoto from './KandidatFoto'
import { odkazNaMedailonek } from '../data/lide'

/**
 * Dlaždice kandidáta: fotka s číslem, jméno a řádek s rolí. Slug jako id
 * je cíl zkratky kandidatN.volbats.cz u toho, kdo medailonek nemá.
 */
export default function KandidatKarta({ kandidat, sizes }) {
  const cil = odkazNaMedailonek(kandidat)

  return (
    <div className="kandidat" id={kandidat.slug}>
      <KandidatFoto kandidat={kandidat} odkaz={cil} sizes={sizes} />
      <div className="kandidat__jmeno">
        {cil ? <Link to={cil}>{kandidat.jmeno}</Link> : kandidat.jmeno}
      </div>
      <div className="kandidat__role">{kandidat.info}</div>
    </div>
  )
}
