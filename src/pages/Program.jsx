import { useState } from 'react'

import Meta from '../components/Meta'
import IkonaSekce from '../components/IkonaSekce'
import VideoTema, { videa, videaPodleSekce } from '../components/VideoTema'
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
  // Které video hraje, ví stránka. Kdyby si to hlídalo každé samo, daly by
  // se spustit dvě naráz a mluvily by přes sebe.
  const [hraje, setHraje] = useState(null)

  const spust = (sekce) => {
    // Při přeskoku na jiné video je potřeba se k němu i posunout;
    // při prvním spuštění by skrolování jen zmátlo.
    if (hraje && hraje !== sekce) {
      document.getElementById(sekce)?.scrollIntoView({ behavior: 'smooth' })
    }
    setHraje(sekce)
  }

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
              <div className="program-sekce__telo">
                <div>
                  {!sekce.nechceme && <p className="program-sekce__uvod">Chceme:</p>}
                  <ul className="program-sekce__body">
                    {sekce.body.map((bod) => (
                      <li key={bod}>{bod}</li>
                    ))}
                  </ul>
                </div>
                {videaPodleSekce[sekce.slug] && (
                  <VideoTema
                    video={videaPodleSekce[sekce.slug]}
                    hraje={hraje === sekce.slug}
                    spust={spust}
                    dalsi={videa[(videaPodleSekce[sekce.slug].poradi + 1) % videa.length]}
                  />
                )}
              </div>
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
