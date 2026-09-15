import Layout from './components/Layout'
import Home from './pages/Home'
import Program from './pages/Program'
import Kandidati from './pages/Kandidati'
import KandidatDetail from './pages/KandidatDetail'
import Kontakt from './pages/Kontakt'
import NotFound from './pages/NotFound'
import { kandidati, maStranku } from './data/lide'
import { starePriority } from './data/stare-adresy'

export const routes = [
  {
    element: <Layout />,
    children: [
      { path: '/', element: <Home /> },
      { path: '/program', element: <Program /> },
      // Priority byly samostatné stránky programu 2022. Program 2026 je má
      // jako sekce jedné stránky, takže staré adresy vedou rovnou na něj —
      // kdo si odkaz uložil, dostane program, ne „stránka nenalezena".
      { path: '/priority', element: <Program /> },
      { path: '/priority/:slug', element: <Program /> },
      { path: '/kandidati', element: <Kandidati /> },
      { path: '/kandidati/:slug', element: <KandidatDetail /> },
      { path: '/kontakt', element: <Kontakt /> },
      { path: '*', element: <NotFound /> },
    ],
  },
]

/**
 * Adresy, které se předgenerují, ale nemají jít do vyhledávačů. Staré adresy
 * priorit ukazují celý program; bez noindex by ho vyhledávače viděly
 * dvacetkrát pod dvaceti adresami.
 */
export const cestyBezIndexu = [
  '/priority/',
  ...starePriority.map((slug) => `/priority/${slug}/`),
]

/** Seznam adres, které se při buildu předgenerují do statického HTML. */
// Adresy končí lomítkem stejně jako odkazy ve webu. Kdyby se předgenerovalo
// pod /kontakt a prohlížeč byl na /kontakt/, NavLink by při prerenderu
// nenašel shodu a po obnovení stránky by menu nemělo zvýrazněnou položku.
export const vsechnyCesty = [
  '/',
  '/program/',
  '/kandidati/',
  ...kandidati.filter(maStranku).map((k) => `/kandidati/${k.slug}/`),
  '/kontakt/',
  ...cestyBezIndexu,
]
