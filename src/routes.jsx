import Layout from './components/Layout'
import Home from './pages/Home'
import Program from './pages/Program'
import ProgramNavrh from './pages/ProgramNavrh'
import Kandidati from './pages/Kandidati'
import KandidatDetail from './pages/KandidatDetail'
import Kontakt from './pages/Kontakt'
import NotFound from './pages/NotFound'
import { kandidati, maStranku } from './data/lide'

export const routes = [
  {
    element: <Layout />,
    children: [
      { path: '/', element: <Home /> },
      { path: '/program', element: <Program /> },
      // Priority jsou součástí programu, takže zmizely spolu s ním. Staré
      // adresy míří na stejné oznámení, ať kdo si je uložil neskončí
      // na „stránka nenalezena".
      { path: '/priority', element: <Program /> },
      { path: '/priority/:slug', element: <Program /> },
      { path: '/program-navrh', element: <ProgramNavrh /> },
      { path: '/kandidati', element: <Kandidati /> },
      { path: '/kandidati/:slug', element: <KandidatDetail /> },
      { path: '/kontakt', element: <Kontakt /> },
      { path: '*', element: <NotFound /> },
    ],
  },
]

/**
 * Adresy, na které se z webu nikde neodkazuje. Prerender jim přidá noindex,
 * aby se pracovní verze programu neobjevila ve vyhledávačích.
 */
export const skryteCesty = ['/program-navrh/']

/** Seznam adres, které se při buildu předgenerují do statického HTML. */
// Adresy končí lomítkem stejně jako odkazy ve webu. Kdyby se předgenerovalo
// pod /kontakt a prohlížeč byl na /kontakt/, NavLink by při prerenderu
// nenašel shodu a po obnovení stránky by menu nemělo zvýrazněnou položku.
export const vsechnyCesty = [
  '/',
  '/program/',
  '/priority/',
  '/kandidati/',
  ...kandidati.filter(maStranku).map((k) => `/kandidati/${k.slug}/`),
  '/kontakt/',
  ...skryteCesty,
]
