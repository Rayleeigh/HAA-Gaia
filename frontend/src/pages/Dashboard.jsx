import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FaServer, FaLayerGroup, FaPlus } from 'react-icons/fa'
import { vmAPI, templateAPI, providerAPI } from '../services/api'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState({
    totalVMs: 0,
    runningVMs: 0,
    templates: 0,
    providers: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [vms, templates, providers] = await Promise.all([
        vmAPI.list(),
        templateAPI.list(),
        providerAPI.list(),
      ])

      const runningVMs = vms.data.filter(vm => vm.state === 'running').length

      setStats({
        totalVMs: vms.data.length,
        runningVMs,
        templates: templates.data.length,
        providers: providers.data.length,
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { label: 'Total VMs', value: stats.totalVMs, icon: FaServer, color: 'blue' },
    { label: 'Running', value: stats.runningVMs, icon: FaServer, color: 'green' },
    { label: 'Templates', value: stats.templates, icon: FaLayerGroup, color: 'purple' },
    { label: 'Providers', value: stats.providers, icon: FaPlus, color: 'orange' },
  ]

  if (loading) {
    return (
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your virtualization environment</p>
      </div>

      <div className="stats-grid">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className={`stat-card stat-${stat.color}`}>
              <div className="stat-icon">
                <Icon />
              </div>
              <div className="stat-content">
                <div className="stat-value">{stat.value}</div>
                <div className="stat-label">{stat.label}</div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="action-cards">
          <Link to="/vms/create" className="action-card">
            <FaPlus className="action-icon" />
            <h3>Create New VM</h3>
            <p>Spin up a new virtual machine</p>
          </Link>

          <Link to="/templates" className="action-card">
            <FaLayerGroup className="action-icon" />
            <h3>Browse Templates</h3>
            <p>View and manage VM templates</p>
          </Link>

          <Link to="/providers" className="action-card">
            <FaPlus className="action-icon" />
            <h3>Configure Providers</h3>
            <p>Manage virtualization providers</p>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
