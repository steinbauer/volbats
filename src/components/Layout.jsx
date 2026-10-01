import { Outlet } from 'react-router-dom'
import Header from './Header'
import Footer from './Footer'
import NahoruPriPrechodu from './NahoruPriPrechodu'
import Mereni from './Mereni'

export default function Layout() {
  return (
    <>
      <NahoruPriPrechodu />
      <Mereni />
      <Header />
      <main>
        <Outlet />
      </main>
      <Footer />
    </>
  )
}
