import { Link } from 'react-router-dom'
import Meta from '../components/Meta'
import { stavProgramu } from '../data/program-stav'
import { web } from '../data/web'

/**
 * Veřejný /program/. Dokud členové o programu hlasují, není tu program, ale
 * vysvětlení proč — adresa zůstává živá, aby odkazy i přímé zkoušení někam
 * vedly. Hotový text čeká na /program-navrh/.
 */
export default function Program() {
  const [prvni, ...zbytek] = stavProgramu.odstavce

  return (
    <>
      <Meta
        title="Program | Volba pro město Trhové Sviny"
        popis="Volební program se dolaďuje — členové sdružení o jednotlivých bodech hlasují."
      />
      <div className="obal">
        <section className="sekce">
          <div className="nadtitulek">{stavProgramu.stitek}</div>
          <h1>{stavProgramu.nadpis}</h1>

          <p className="uvod__perex mt-4">{prvni}</p>

          <div className="text uzky">
            {zbytek.map((odstavec) => (
              <p key={odstavec}>{odstavec}</p>
            ))}
            <p>
              Máte k programu co říct? Napište nám na{' '}
              <a href={`mailto:${web.email}`}>{web.email}</a>.
            </p>
          </div>

          <div className="uvod__akce mt-4">
            <Link className="tlacitko tlacitko--plne" to="/kandidati/">
              Poznejte naše kandidáty
            </Link>
            <Link className="tlacitko tlacitko--obrys" to="/kontakt/">
              Kontakt
            </Link>
          </div>
        </section>
      </div>
    </>
  )
}
