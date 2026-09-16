import Meta from '../components/Meta'
import IkonaSekce from '../components/IkonaSekce'
import program from '../data/program.json'
import { web } from '../data/web'

/**
 * Celý volební program na jedné stránce.
 *
 * Sekce jsou krátké (dvě až šest odrážek), takže na vlastní podstránky se
 * nedělí — proklikat patnáct stránek po třech větách by byla otrava.
 * Rozcestník nahoře skáče na kotvy, na stejné kotvy míří i dlaždice
 * na úvodní stránce.
 */
export default function Program() {
  return (
    <>
      {/* Popisek je psaný zvlášť, ne slepený z perexu a úvodu — ty dají
          dohromady přes tři sta znaků a vyhledávač je stejně usekne. */}
      <Meta
        title="Program | Volba pro město Trhové Sviny"
        popis={
          'Volební program sdružení Volba pro město Trhové Sviny pro komunální ' +
          'volby 2026 — rozvoj města, děti, senioři, doprava, zdravotnictví, ' +
          'místní části i účelné hospodaření.'
        }
      />
      <div className="obal">
        <section className="sekce">
          <h1>Náš program</h1>

          <p className="uvod__perex mt-4">{program.perex}</p>
          <div className="text mt-3">
            <p>{program.uvod}</p>
          </div>

          <nav className="program__obsah" aria-label="Obsah programu">
            {program.sekce.map((s) => (
              <a href={`#${s.slug}`} key={s.slug}>
                <IkonaSekce slug={s.slug} className="program__obsah-ikona" />
                {s.stitek}
              </a>
            ))}
          </nav>

          <div className="papir program__sekce-obal">
          {program.sekce.map((sekce) => (
            <article
              className={`program-sekce${sekce.nechceme ? ' program-sekce--ne' : ''}`}
              id={sekce.slug}
              key={sekce.slug}
            >
              {/* Čísla 01, 02, 03 sekce dřív jen přeříkávala pořadí. Teď
                  je místo nich kresba tématu — pozná se od oka, o co jde,
                  a je to stejný rukopis jako srdce z loga. */}
              <h2>
                <IkonaSekce slug={sekce.slug} className="program-sekce__ikona" />
                {sekce.nadpis}
              </h2>
              {!sekce.nechceme && <p className="program-sekce__uvod">Chceme:</p>}
              <ul className="program-sekce__body">
                {sekce.body.map((bod) => (
                  <li key={bod}>{bod}</li>
                ))}
              </ul>
            </article>
          ))}
          </div>

          <div className="program__zaver">
            <h2>{program.zaver}</h2>
            <p>
              Napište nám na <a href={`mailto:${web.email}`}>{web.email}</a>.
            </p>
          </div>
        </section>
      </div>
    </>
  )
}
