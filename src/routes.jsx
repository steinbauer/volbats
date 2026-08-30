import Layout from './components/Layout'
import Home from './pages/Home'
import Priority from './pages/Priority'
import PriorityDetail from './pages/PriorityDetail'
import Program from './pages/Program'
import Kandidati from './pages/Kandidati'
import KandidatDetail from './pages/KandidatDetail'
import Kontakt from './pages/Kontakt'
import NotFound from './pages/NotFound'
import priority from './data/priority.json'
import kandidati from './data/kandidati.json'

export const routes = [
  {
    element: <Layout />,
    children: [
      { path: '/', element: <Home /> },
      { path: '/priority', element: <Priority /> },
      { path: '/priority/:slug', element: <PriorityDetail /> },
      { path: '/program', element: <Program /> },
      { path: '/kandidati', element: <Kandidati /> },
      { path: '/kandidati/:slug', element: <KandidatDetail /> },
      { path: '/kontakt', element: <Kontakt /> },
      { path: '*', element: <NotFound /> },
    ],
  },
]

/** Seznam adres, které se při buildu předgenerují do statického HTML. */
// Adresy končí lomítkem stejně jako odkazy ve webu. Kdyby se předgenerovalo
// pod /kontakt a prohlížeč byl na /kontakt/, NavLink by při prerenderu
// nenašel shodu a po obnovení stránky by menu nemělo zvýrazněnou položku.
export const vsechnyCesty = [
  '/',
  '/priority/',
  ...priority.map((p) => `/priority/${p.slug}/`),
  '/program/',
  '/kandidati/',
  ...kandidati.filter((k) => k.slug).map((k) => `/kandidati/${k.slug}/`),
  '/kontakt/',
]
