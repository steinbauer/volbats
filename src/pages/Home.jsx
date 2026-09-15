import { Link } from 'react-router-dom'
import Meta from '../components/Meta'
import Prose from '../components/Prose'
import Galerie from '../components/Galerie'
import CisloSrdce from '../components/CisloSrdce'
import KandidatKarta from '../components/KandidatKarta'
import { obrazek } from '../obrazky'
import { web } from '../data/web'
import stranky from '../data/stranky.json'
import program from '../data/program.json'
import { kandidati } from '../data/lide'

// Šířky, ve kterých tools/fotky.py ukládá společnou fotku
const SIRKY_SPOLECNA = [800, 1400, 2000, 2600]

// Osm dlaždic zaplní dva řádky mřížky; na zbytek vede odkaz pod nimi
const DLAZDIC = 8

// Pás kandidátů na úvodní stránce má pět sloupců, na užších displejích méně
const SIZES_PAS =
  '(min-width: 1200px) 250px, (min-width: 992px) 26vw, (min-width: 768px) 30vw, 45vw'

// Úvodní odstavec putuje do hlavičky stránky jako perex, zbytek zůstává
// v textovém bloku pod fotkou — ať se stejná věta neopakuje dvakrát.
//
// Text je ze starého CMS zabalený do šesti <div>. Ukrojit ho podle prvního
// </p> by je nechalo neuzavřené a prohlížeč si je při vložení přes innerHTML
// domyslí jinam než server — hydratace se rozešla a React překresloval celou
// stránku znovu. Bereme proto samotný první odstavec a ze zbytku ho
// vyřízneme, takže obě půlky mají tagy spárované.
const prvniOdstavec = stranky.home.html.match(/<p>[\s\S]*?<\/p>/)
const perex = prvniOdstavec?.[0] ?? ''
const zbytekTextu = prvniOdstavec
  ? stranky.home.html.replace(prvniOdstavec[0], '')
  : stranky.home.html

export default function Home() {
  return (
    <>
      <Meta title={`${web.nazev} ${web.mesto}`} />

      <div className="obal">
        <div className="uvod">
          <div>
            <div className="nadtitulek">Komunální volby v Trhových Svinech</div>
            <h1>{web.claim}</h1>
            <Prose className="uvod__perex" html={perex} />
            <div className="uvod__akce">
              <Link className="tlacitko tlacitko--plne" to="/program/">
                Prohlédnout program
              </Link>
              <Link className="tlacitko tlacitko--obrys" to="/kandidati/">
                {kandidati.length} kandidátů
              </Link>
            </div>
          </div>

          <CisloSrdce />
        </div>
      </div>

      <div className="obal spolecna-fotka">
        {/* Ukazuje se celá, bez ořezu v prohlížeči — proto jen zmenšeniny
            v několika šířkách a žádná pevná výška. */}
        <img
          src={obrazek('spolecna-1400.webp')}
          srcSet={SIRKY_SPOLECNA.map((w) => `${obrazek(`spolecna-${w}.webp`)} ${w}w`).join(', ')}
          sizes="(min-width: 1440px) 1296px, 92vw"
          alt={`Kandidáti sdružení ${web.nazev} ${web.mesto}`}
        />
      </div>

      <div className="obal">
        <section className="sekce pt-0">
          <div className="text">
            <Prose html={zbytekTextu} />
          </div>
          <Galerie />
        </section>
      </div>

      {/* Tmavý pás drží rytmus stránky bílá — tmavá — bílá. Dlaždice míří
          na kotvy v programu, ne na vlastní podstránky: sekce jsou krátké
          a rozpadat je na patnáct stránek by nikomu nepomohlo. */}
      <section className="program-tmave">
        <div className="obal">
          <h2>Náš program</h2>
          <p className="program-tmave__perex">{program.uvod}</p>

          <div className="dlazdice-programu">
            {program.sekce.slice(0, DLAZDIC).map((sekce, i) => (
              <Link to={`/program/#${sekce.slug}`} key={sekce.slug}>
                <span className="dlazdice-programu__cislo">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span className="dlazdice-programu__nazev">{sekce.stitek}</span>
              </Link>
            ))}
          </div>

          <p className="mt-4 mb-0">
            <Link className="sekce__odkaz" style={{ color: '#eed239' }} to="/program/">
              Celý program →
            </Link>
          </p>
        </div>
      </section>

      <div className="obal">
        <section className="sekce">
          <div className="sekce__hlavicka">
            <h2>Lidé na kandidátce</h2>
            <Link className="sekce__odkaz" to="/kandidati/">
              Všech {kandidati.length} →
            </Link>
          </div>

          <div className="mrizka-kandidatu mrizka-kandidatu--pas">
            {kandidati.slice(0, 10).map((k) => (
              <KandidatKarta kandidat={k} sizes={SIZES_PAS} key={k.cislo} />
            ))}
          </div>
        </section>
      </div>
    </>
  )
}
