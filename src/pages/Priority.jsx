import { Link } from 'react-router-dom'
import Stranka from './Stranka'
import stranky from '../data/stranky.json'
import priority from '../data/priority.json'

export default function Priority() {
  return (
    <Stranka nadpis={stranky.priority.nadpis} html={stranky.priority.html}>
      <div className="downmenu">
        <ul>
          {priority.map((p) => (
            <li key={p.slug}>
              <Link to={`/priority/${p.slug}`}>{p.nadpis}</Link>
            </li>
          ))}
        </ul>
      </div>
    </Stranka>
  )
}
