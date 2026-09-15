import { Link, useParams } from 'react-router-dom'
import Meta from '../components/Meta'
import Prose from '../components/Prose'
import KandidatFoto from '../components/KandidatFoto'
import { kandidati, maStranku } from '../data/lide'
import NotFound from './NotFound'

export default function KandidatDetail() {
  const { slug } = useParams()
  const sStrankou = kandidati.filter(maStranku)
  const poradi = sStrankou.findIndex((k) => k.slug === slug)
  if (poradi === -1) return <NotFound />

  const kandidat = sStrankou[poradi]
  const dalsi = sStrankou[(poradi + 1) % sStrankou.length]

  return (
    <>
      {/* Samotné „důchodce, 72 let" je jako popisek ve výsledku hledání
          málo — doplňujeme jméno a pořadí. Tvar „č. N na kandidátce" je tu
          schválně místo „kandidát/kandidátka", ať to sedí na všechny. */}
      <Meta
        title={`${kandidat.jmeno} | Volba pro město Trhové Sviny`}
        popis={
          `${kandidat.jmeno} — ${kandidat.info}. Č. ${kandidat.cislo} ` +
          'na kandidátce sdružení Volba pro město Trhové Sviny.'
        }
      />

      <div className="obal">
        <div className="medailonek">
          <div className="medailonek__foto">
            <KandidatFoto
              kandidat={kandidat}
              sizes="(min-width: 1200px) 420px, (min-width: 768px) 30vw, 92vw"
            />

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

          <div className="medailonek__obsah">
            <div className="medailonek__hlavicka">
              <div className="nadtitulek">Kandidát č. {kandidat.cislo}</div>
              <h1>{kandidat.jmeno}</h1>
              <p className="medailonek__role mt-3">{kandidat.info}</p>
            </div>

            <div className="medailonek__telo">
              <div className="text">
                <Prose html={kandidat.zivotopis} />
              </div>

              <div className="medailonek__navigace mt-5">
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
      </div>
    </>
  )
}
