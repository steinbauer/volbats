import { Link } from 'react-router-dom'
import { obrazek } from '../obrazky'

/**
 * Dlaždice kandidáta s pořadovým číslem. Jen část kandidátů má medailonek —
 * u ostatních se jméno a fotka nelinkují.
 */
export default function KandidatKarta({ kandidat }) {
  const { cislo, jmeno, slug, foto, info } = kandidat
  const cil = slug ? `/kandidati/${slug}` : null
  const fotka = <img src={obrazek(foto)} alt={jmeno} className="img-fluid" />

  return (
    <div className="thumbnail">
      <div className="ratio ratio-kandidat">
        <div className="ramecek">{cil ? <Link to={cil}>{fotka}</Link> : fotka}</div>
        {cislo != null && <div className="cislo">{cislo}</div>}
      </div>

      <div className="caption">
        <h4>{cil ? <Link to={cil}>{jmeno}</Link> : jmeno}</h4>
        <p className="peopleInfo">{info}</p>
      </div>
    </div>
  )
}
