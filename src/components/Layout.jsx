import { Outlet } from 'react-router-dom'
import Header from './Header'
import Footer from './Footer'
import NahoruPriPrechodu from './NahoruPriPrechodu'

export default function Layout() {
  return (
    <>
      <NahoruPriPrechodu />
      <Header />
      <main>
        <Outlet />
      </main>
      <Footer />
    </>
  )
}
