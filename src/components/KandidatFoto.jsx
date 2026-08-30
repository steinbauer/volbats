import { Link } from 'react-router-dom'
import { obrazek } from '../obrazky'

/** Fotka kandidáta s pořadovým číslem v rohu. */
export default function KandidatFoto({ kandidat, odkaz }) {
  const fotka = <img src={obrazek(kandidat.foto)} alt={kandidat.jmeno} loading="lazy" />

  return (
    <div className="kandidat__foto">
      {odkaz ? <Link to={odkaz}>{fotka}</Link> : fotka}
      {kandidat.cislo != null && <div className="kandidat__cislo">{kandidat.cislo}</div>}
    </div>
  )
}
