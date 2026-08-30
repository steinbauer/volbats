import { Link } from 'react-router-dom'
import KandidatFoto from './KandidatFoto'

/** Dlaždice kandidáta: fotka s číslem, jméno a řádek s rolí. */
export default function KandidatKarta({ kandidat }) {
  const cil = kandidat.slug ? `/kandidati/${kandidat.slug}/` : null

  return (
    <div className="kandidat">
      <KandidatFoto kandidat={kandidat} odkaz={cil} />
      <div className="kandidat__jmeno">
        {cil ? <Link to={cil}>{kandidat.jmeno}</Link> : kandidat.jmeno}
      </div>
      <div className="kandidat__role">{kandidat.info}</div>
    </div>
  )
}
