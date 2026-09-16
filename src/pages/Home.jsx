import { Link } from 'react-router-dom'
import Meta from '../components/Meta'
import Prose from '../components/Prose'
import Galerie from '../components/Galerie'
import IkonaSekce from '../components/IkonaSekce'
import Znak from '../components/Znak'
import { obrazek, sirky } from '../obrazky'
import { web } from '../data/web'
import stranky from '../data/stranky.json'
import program from '../data/program.json'

// Šířky, ve kterých společná fotka opravdu je — podle toho, jak velkou
// předlohu jsme dostali
const SIRKY_SPOLECNA = sirky('spolecna')

// Úvodní odstavec putuje nad fotku jako perex, zbytek zůstává v textovém
// bloku níž — ať se stejná věta neopakuje dvakrát.
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

      {/* Fotka začíná hned pod hlavičkou a logo do ní shora zasahuje —
          proto je ořezaná jen zespodu a nad lidmi jí zbývá kus náměstí.
          Horní okraj se přelévá do plochy stránky, aby logo nesedělo
          v barevném zmatku fasád. */}
      <div className="uvodni-fotka">
        <img
          src={obrazek(`spolecna-${SIRKY_SPOLECNA.at(-1)}.webp`)}
          srcSet={SIRKY_SPOLECNA.map((w) => `${obrazek(`spolecna-${w}.webp`)} ${w}w`).join(', ')}
          sizes="100vw"
          alt={`Kandidáti sdružení ${web.nazev} ${web.mesto}`}
          fetchPriority="high"
        />
      </div>

      <div className="obal">
        <div className="uvod">
          <h1>{web.titulek}</h1>
          <Prose className="uvod__perex" html={perex} />
        </div>
      </div>

      {/* Volební číslo. V hlavičce je značka, tady číslo — stejné rozdělení
          rolí jako na letáku. Srdce je tu jen nosičem přechodu, číslo v něm
          podruhé by vedle velké číslice nedávalo smysl. */}
      <div className="obal">
        <div className="volte">
          <Znak className="volte__znak" sikmo aria-hidden="true" />
          <div>
            <div className="volte__popisek">Volte číslo</div>
            <div className="volte__cislo">{web.cislo}</div>
          </div>
          <div className="volte__termin">
            Komunální volby
            <strong>{web.termin}</strong>
          </div>
        </div>
      </div>

      <div className="obal">
        <section className="sekce">
          <div className="text papir">
            <Prose html={zbytekTextu} />
          </div>

          {/* Jediný blok s lidmi na stránce. Dřív byl ještě jeden níž
              s deseti jmény, ale dvakrát po sobě titíž lidé nikomu nic
              nepřidaly. */}
          <Galerie />
          <p className="galerie__akce">
            <Link className="tlacitko tlacitko--plne" to="/kandidati/">
              Naši kandidáti
            </Link>
          </p>
        </section>
      </div>

      {/* Tmavý pás drží rytmus stránky světlá — tmavá — světlá. Dlaždice míří
          na kotvy v programu, ne na vlastní podstránky: sekce jsou krátké
          a rozpadat je na patnáct stránek by nikomu nepomohlo. */}
      <section className="program-tmave">
        <div className="obal">
          <h2>Náš program</h2>
          <p className="program-tmave__perex">{program.uvod}</p>

          {/* Všech patnáct témat, ne jen výběr — mřížka je stejně dlouhá jako
              program sám a návštěvník rovnou vidí, co všechno pokrývá. */}
          <div className="dlazdice-programu">
            {program.sekce.map((sekce) => (
              <Link to={`/program/#${sekce.slug}`} key={sekce.slug}>
                <IkonaSekce slug={sekce.slug} className="dlazdice-programu__ikona" />
                <span className="dlazdice-programu__nazev">{sekce.stitek}</span>
              </Link>
            ))}
            <Link to="/program/">
              <span className="dlazdice-programu__vic">Celý program →</span>
            </Link>
          </div>
        </div>
      </section>
    </>
  )
}
