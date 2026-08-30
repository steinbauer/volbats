import Prose from './Prose'
import tabulka from '../data/program-tabulka.json'

/**
 * Dvousloupcová bilance „Podařilo se / Chceme". Popisky sloupců jsou
 * v hlavičce, na úzkém displeji se místo ní ukáže popisek u každé buňky.
 */
export default function Bilance({ radky = tabulka }) {
  return (
    <div className="bilance">
      <div className="bilance__hlavicka">
        <div>{radky[0]?.[0]?.nadpis ?? 'Podařilo se'}</div>
        <div>{radky[0]?.[1]?.nadpis ?? 'Chceme'}</div>
      </div>

      {radky.map((radek, i) => (
        <div className="bilance__radek" key={i}>
          {radek.map((sloupec, j) => (
            <div className="bilance__sloupec" key={j}>
              <div className={`bilance__popisek${j ? ' bilance__popisek--chceme' : ''}`}>
                {sloupec.nadpis}
              </div>
              <Prose html={sloupec.html} />
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
