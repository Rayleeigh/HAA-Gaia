import { Link, useLocation } from 'react-router-dom'
import { FaServer, FaLayerGroup, FaPlug, FaHome } from 'react-icons/fa'
import './Layout.css'

function Layout({ children }) {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: FaHome },
    { path: '/vms', label: 'Virtual Machines', icon: FaServer },
    { path: '/templates', label: 'Templates', icon: FaLayerGroup },
    { path: '/providers', label: 'Providers', icon: FaPlug },
  ]

  return (
    <div className="layout">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1 className="logo">HAA-Gaia</h1>
          <p className="logo-subtitle">VM Orchestration</p>
        </div>

        <ul className="nav-menu">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path

            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`nav-link ${isActive ? 'active' : ''}`}
                >
                  <Icon className="nav-icon" />
                  <span>{item.label}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout
