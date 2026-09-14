import { Link } from 'react-router-dom'
import Meta from '../components/Meta'
import Prose from '../components/Prose'
import Galerie from '../components/Galerie'
import StavProgramu from '../components/StavProgramu'
import CisloSrdce from '../components/CisloSrdce'
import KandidatKarta from '../components/KandidatKarta'
import { obrazek } from '../obrazky'
import { web } from '../data/web'
import stranky from '../data/stranky.json'
import { kandidati } from '../data/lide'

// Šířky, ve kterých tools/fotky.py ukládá společnou fotku
const SIRKY_SPOLECNA = [800, 1400, 2000, 2600]

// Pás kandidátů na úvodní stránce má pět sloupců, na užších displejích méně
const SIZES_PAS =
  '(min-width: 1200px) 250px, (min-width: 992px) 26vw, (min-width: 768px) 30vw, 45vw'

// Úvodní odstavec putuje do hlavičky stránky jako perex, zbytek zůstává
// v textovém bloku pod fotkou — ať se stejná věta neopakuje dvakrát.
const konec = stranky.home.html.indexOf('</p>')
const perex = stranky.home.html.slice(0, konec + 4)
const zbytekTextu = stranky.home.html.slice(konec + 4)

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
            {/* Dokud se program dolaďuje, nemá první tlačítko kam vést —
                nejsilnější, co teď máme, je kandidátka. */}
            <div className="uvod__akce">
              <Link className="tlacitko tlacitko--plne" to="/kandidati/">
                {kandidati.length} kandidátů
              </Link>
              <Link className="tlacitko tlacitko--obrys" to="/kontakt/">
                Napište nám
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

      <StavProgramu />

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
