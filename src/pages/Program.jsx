import Meta from '../components/Meta'
import program from '../data/program.json'
import { web } from '../data/web'

// „Nechceme" se nečísluje — není to další v pořadí, je to protiváha
// všeho, co je nad ním.
const cislovane = program.sekce.filter((s) => !s.nechceme)

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
          <div className="nadtitulek">Komunální volby {web.termin}</div>
          <h1>Náš program</h1>

          <p className="uvod__perex mt-4">{program.perex}</p>
          <div className="text uzky">
            <p>{program.uvod}</p>
          </div>

          <nav className="program__obsah" aria-label="Obsah programu">
            {program.sekce.map((s) => (
              <a href={`#${s.slug}`} key={s.slug}>
                {s.stitek}
              </a>
            ))}
          </nav>

          {program.sekce.map((sekce) => (
            <article
              className={`program-sekce${sekce.nechceme ? ' program-sekce--ne' : ''}`}
              id={sekce.slug}
              key={sekce.slug}
            >
              <h2>
                {!sekce.nechceme && (
                  <span className="program-sekce__cislo">
                    {String(cislovane.indexOf(sekce) + 1).padStart(2, '0')}
                  </span>
                )}
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
