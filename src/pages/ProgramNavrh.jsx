import { Link } from 'react-router-dom'
import Meta from '../components/Meta'
import Prose from '../components/Prose'
import ProgramBody from '../components/ProgramBody'
import stranky from '../data/stranky.json'
import priority from '../data/priority.json'

/**
 * Pracovní verze programu pro lídryni.
 *
 * Neveřejná: není v menu, nikde na webu na ni nevede odkaz a prerender jí
 * do hlavičky přidá noindex (tools/prerender.js, seznam skryteCesty
 * v routes.jsx). Všechno je schválně na jedné stránce — dolaďuje se lépe
 * ve scrollu než proklikáváním devatenácti podstránek.
 */
export default function ProgramNavrh() {
  return (
    <>
      <Meta
        title="Pracovní verze programu (neveřejné)"
        popis="Pracovní verze volebního programu, není určená ke zveřejnění."
      />
      <div className="obal">
        <section className="sekce">
          <div className="pracovni-verze">
            <strong>Pracovní verze, nezveřejňovat.</strong> Stránka není
            v menu, nikde na webu na ni nevede odkaz a vyhledávače ji mají
            zakázanou. Veřejná adresa <Link to="/program/">/program/</Link>{' '}
            zatím ukazuje jen oznámení, že se program dolaďuje.
          </div>

          <h1>{stranky.program.nadpis}</h1>
          <div className="text mt-4 mb-5">
            <Prose html={stranky.program.html} />
          </div>

          <h2 className="navrh__nadpis">Body programu</h2>
          <ProgramBody />

          <h2 className="navrh__nadpis mt-5">{priority.length} priorit</h2>
          <ol className="navrh__obsah">
            {priority.map((p) => (
              <li key={p.slug}>
                <a href={`#${p.slug}`}>{p.nadpis}</a>
              </li>
            ))}
          </ol>

          {priority.map((p, i) => (
            <article className="navrh__priorita" id={p.slug} key={p.slug}>
              <h3>
                <span className="navrh__cislo">{String(i + 1).padStart(2, '0')}</span>
                {p.nadpis}
              </h3>
              <div className="text">
                <Prose html={p.html} />
              </div>
            </article>
          ))}
        </section>
      </div>
    </>
  )
}
