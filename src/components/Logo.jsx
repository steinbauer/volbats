import { CESTA, VIEWBOX } from './Znak'
import { web } from '../data/web'

/**
 * Logo sdružení tak, jak ho má leták: název, město a claim vysázené uvnitř
 * srdce. Text má v srdci k dispozici asi 800 jednotek šířky, takže pod
 * zhruba 140 px se přestane dát číst — menší místa (hlavička podstránek,
 * patička) proto sázejí název vedle srdce, viz `.logo` v šabloně.
 *
 * Písmo je z webu, ne z letáku: leták má patkovou serifu, kterou tu nemáme
 * a dokupovat ji kvůli logu by bylo zbytečné. Obtažené jsou křivky srdce,
 * text je sazba.
 */
export default function Logo({ className, ...zbytek }) {
  return (
    <svg
      className={className}
      viewBox={VIEWBOX}
      role="img"
      aria-label={`${web.nazev} ${web.mesto} — ${web.claim}`}
      {...zbytek}
    >
      {CESTA.map((d, i) => (
        <path key={i} d={d} fill="#c23a22" />
      ))}
      <text className="logo-znak__nazev" x="522" y="258" textAnchor="middle">
        {web.nazev}
      </text>
      <text className="logo-znak__mesto" x="522" y="362" textAnchor="middle">
        {web.mesto}
      </text>
      <text className="logo-znak__claim" x="522" y="440" textAnchor="middle">
        {web.claim}
      </text>
    </svg>
  )
}
