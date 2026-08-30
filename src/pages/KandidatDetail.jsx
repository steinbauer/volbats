import { Link, useParams } from 'react-router-dom'
import Meta from '../components/Meta'
import Prose from '../components/Prose'
import KandidatFoto from '../components/KandidatFoto'
import kandidati from '../data/kandidati.json'
import NotFound from './NotFound'

export default function KandidatDetail() {
  const { slug } = useParams()
  const poradi = kandidati.findIndex((k) => k.slug === slug)
  if (poradi === -1) return <NotFound />

  const kandidat = kandidati[poradi]
  const dalsi = kandidati[(poradi + 1) % kandidati.length]

  return (
    <>
      <Meta
        title={`${kandidat.jmeno} | Volba pro město Trhové Sviny`}
        popis={kandidat.info}
      />

      <div className="obal">
        <div className="medailonek">
          <div className="medailonek__foto">
            <KandidatFoto kandidat={kandidat} />

            <dl className="udaje">
              <div>
                <dt>Povolání</dt>
                <dd>{kandidat.povolani}</dd>
              </div>
              <div>
                <dt>Bydliště</dt>
                <dd>{kandidat.cast}</dd>
              </div>
              <div>
                <dt>Politická příslušnost</dt>
                <dd>{kandidat.strana}</dd>
              </div>
              <div>
                <dt>Věk ke druhému dni voleb</dt>
                <dd>{kandidat.vek} let</dd>
              </div>
            </dl>
          </div>

          <div>
            <div className="nadtitulek">Kandidát č. {kandidat.cislo}</div>
            <h1>{kandidat.jmeno}</h1>
            <p className="medailonek__role mt-3">{kandidat.info}</p>

            <div className="text">
              {kandidat.zivotopis ? (
                <Prose html={kandidat.zivotopis} />
              ) : (
                <p className="pripravuje">Medailonek se připravuje.</p>
              )}
            </div>

            <div className="uvod__akce mt-5">
              <Link className="tlacitko tlacitko--obrys" to="/kandidati/">
                ← Zpět na kandidátku
              </Link>
              <Link className="tlacitko tlacitko--plne" to={`/kandidati/${dalsi.slug}/`}>
                {dalsi.jmeno} →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
