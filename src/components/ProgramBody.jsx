import Prose from './Prose'
import body from '../data/program-body.json'

/**
 * Body programu pod sebou.
 *
 * Dřív to byla dvousloupcová bilance „Podařilo se / Chceme". Lídryně
 * 31. 8. 2026 napsala, že se dosažené věci vynechají a zůstane jen program,
 * takže zbyly samotné závazky. Jeden bod je „Nechceme" — ten se odlišuje,
 * u ostatních by se popisek „Chceme“ jen patnáctkrát opakoval.
 */
export default function ProgramBody({ body: seznam = body }) {
  return (
    <div className="program">
      {seznam.map((bod, i) => (
        <div className="program__bod" key={i}>
          <span className="program__cislo">{String(i + 1).padStart(2, '0')}</span>
          <div>
            {bod.nadpis !== 'Chceme' && (
              <div className="program__popisek">{bod.nadpis}</div>
            )}
            <Prose html={bod.html} />
          </div>
        </div>
      ))}
    </div>
  )
}
