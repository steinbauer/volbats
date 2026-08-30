import { useParams } from 'react-router-dom'
import Stranka from './Stranka'
import priority from '../data/priority.json'
import NotFound from './NotFound'

export default function PriorityDetail() {
  const { slug } = useParams()
  const polozka = priority.find((p) => p.slug === slug)
  if (!polozka) return <NotFound />

  return <Stranka nadpis={polozka.nadpis} html={polozka.html} />
}
