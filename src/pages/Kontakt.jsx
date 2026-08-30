import Stranka from './Stranka'
import stranky from '../data/stranky.json'
import { web } from '../data/web'

/**
 * Kontakt. Formulář tu dřív byl, ale odesílal data na server PolyWeb CMS —
 * statický web žádný nemá a poštovní adresa splní totéž bez závislosti
 * na cizí službě.
 */
export default function Kontakt() {
  return (
    <Stranka nadpis={stranky.kontakt.nadpis}>
      <p>
        Napište nám na <a href={`mailto:${web.email}`}>{web.email}</a>.
        Rádi odpovíme.
      </p>

      <p>
        <strong>Lídr sdružení:</strong>
        <br />
        {web.lidr}
        <br />
        e-mail: <a href={`mailto:${web.email}`}>{web.email}</a>
      </p>
    </Stranka>
  )
}
