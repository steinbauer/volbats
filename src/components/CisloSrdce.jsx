import { web } from '../data/web'
import Znak from './Znak'

/** Volební číslo posazené do srdce z loga. */
export default function CisloSrdce() {
  return (
    <div className="cislo-srdce">
      <Znak sikmo aria-hidden="true" />
      <div className="cislo-srdce__text">
        <div className="cislo-srdce__popisek">volte číslo</div>
        <div className="cislo-srdce__cislo">{web.cislo}</div>
      </div>
    </div>
  )
}
