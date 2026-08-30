import { Link } from 'react-router-dom'
import Meta from '../components/Meta'
import Prose from '../components/Prose'
import Galerie from '../components/Galerie'
import Bilance from '../components/Bilance'
import CisloSrdce from '../components/CisloSrdce'
import KandidatKarta from '../components/KandidatKarta'
import { obrazek } from '../obrazky'
import { web } from '../data/web'
import stranky from '../data/stranky.json'
import priority from '../data/priority.json'
import kandidati from '../data/kandidati.json'
import tabulka from '../data/program-tabulka.json'

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
        <img
          src={obrazek('kandidati-volbats.jpg')}
          alt={`Kandidáti sdružení ${web.nazev}`}
        />
      </div>

      <div className="obal">
        <section className="sekce pt-0">
          <div className="text">
            <Prose html={zbytekTextu} />
          </div>
          <Galerie />
        </section>

        <section className="sekce">
          <div className="sekce__hlavicka">
            <h2>Bilance, ne sliby</h2>
            <Link className="sekce__odkaz" to="/program/">
              Celý program →
            </Link>
          </div>
          <Bilance radky={tabulka.slice(0, 3)} />
        </section>
      </div>

      <section className="priority-tmave">
        <div className="obal">
          <h2>{priority.length} priorit</h2>
          <p className="priority-tmave__perex">
            Od hospodaření města po místní části. Každá má svou stránku, kde je
            konkrétně napsáno, co s ní chceme dělat.
          </p>

          <div className="dlazdice-priorit">
            {priority.slice(0, 8).map((p, i) => (
              <Link to={`/priority/${p.slug}/`} key={p.slug}>
                <span className="dlazdice-priorit__cislo">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span className="dlazdice-priorit__nazev">{p.nadpis}</span>
              </Link>
            ))}
          </div>

          <p className="mt-4 mb-0">
            <Link className="sekce__odkaz" style={{ color: '#eed239' }} to="/priority/">
              Všech {priority.length} priorit →
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
            {kandidati.slice(0, 6).map((k) => (
              <KandidatKarta kandidat={k} key={k.cislo} />
            ))}
          </div>
        </section>
      </div>
    </>
  )
}
