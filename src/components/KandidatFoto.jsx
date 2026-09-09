import { Link } from 'react-router-dom'
import { obrazek } from '../obrazky'

// Šířky, ve kterých tools/fotky.py fotky ukládá
const SIRKY = [400, 800, 1200]

/**
 * Fotka kandidáta s pořadovým číslem v rohu.
 *
 * Portréty jsou uložené ve třech velikostech; přes srcset si prohlížeč sám
 * stáhne tu, kterou v daném místě opravdu zobrazí, takže se na mobilu netahá
 * dvanáctistovka. `sizes` říká, jak široko se fotka v daném kontextu vykreslí.
 */
export default function KandidatFoto({ kandidat, odkaz, sizes = '100vw' }) {
  const { foto, jmeno } = kandidat
  const maVarianty = foto && !foto.includes('.')

  const fotka = maVarianty ? (
    <img
      src={obrazek(`${foto}-800.webp`)}
      srcSet={SIRKY.map((w) => `${obrazek(`${foto}-${w}.webp`)} ${w}w`).join(', ')}
      sizes={sizes}
      alt={jmeno}
      loading="lazy"
    />
  ) : (
    <img src={obrazek(foto)} alt={jmeno} loading="lazy" />
  )

  return (
    <div className="kandidat__foto">
      {odkaz ? <Link to={odkaz}>{fotka}</Link> : fotka}
      {kandidat.cislo != null && <div className="kandidat__cislo">{kandidat.cislo}</div>}
    </div>
  )
}
