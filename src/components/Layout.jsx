import { Outlet } from 'react-router-dom'
import Header from './Header'
import Nav from './Nav'
import Footer from './Footer'

export default function Layout() {
  return (
    <div className="all">
      <Header />
      <Outlet />
      <Footer />
    </div>
  )
}
