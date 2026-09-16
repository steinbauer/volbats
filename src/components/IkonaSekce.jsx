import { useId } from 'react'
import ikony from '../data/ikony.json'

/**
 * Ikona sekce programu. Kresby vyrábí tools/ikony.py do src/data/ikony.json,
 * klíčem je slug sekce — dokud sekce ikonu nemá, nevykreslí se nic a místo
 * po ní nezůstane.
 *
 * Tahy mají proměnlivou šířku a dobíhají do špičky, stejně jako oblouky
 * srdce z loga. Uzavřené tahy (štít, mince) jsou dva prstence nad sebou,
 * proto fill-rule evenodd.
 */
export default function IkonaSekce({ slug, className }) {
  const id = useId()
  const tahy = ikony[slug]
  if (!tahy) return null

  return (
    <svg className={className} viewBox="0 0 100 100" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#eed239" />
          <stop offset="1" stopColor="#dd4c2f" />
        </linearGradient>
      </defs>
      {tahy.map((d, i) => (
        <path key={i} d={d} fill={`url(#${id})`} fillRule="evenodd" />
      ))}
    </svg>
  )
}
