import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FaCheck, FaTimes, FaPlug, FaCog } from 'react-icons/fa'
import { providerAPI } from '../services/api'

function Providers() {
  const [providers, setProviders] = useState([])
  const [statuses, setStatuses] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProviders()
  }, [])

  const loadProviders = async () => {
    try {
      const response = await providerAPI.list()
      setProviders(response.data)

      // Load status for each provider
      const statusPromises = response.data.map((p) =>
        providerAPI.getStatus(p.name).catch(() => ({
          data: { available: false, configured: false },
        }))
      )
      const statusResults = await Promise.all(statusPromises)

      const statusMap = {}
      response.data.forEach((p, i) => {
        statusMap[p.name] = statusResults[i].data
      })
      setStatuses(statusMap)
    } catch (error) {
      console.error('Failed to load providers:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Providers</h1>
          <p>Manage virtualization provider integrations</p>
        </div>
        <Link to="/providers/settings" className="btn btn-primary">
          <FaCog /> Configure Providers
        </Link>
      </div>

      <div className="grid grid-cols-2">
        {providers.map((provider) => {
          const status = statuses[provider.name] || {}

          return (
            <div key={provider.name} className="card">
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div
                  style={{
                    width: '60px',
                    height: '60px',
                    borderRadius: '0.5rem',
                    background: 'var(--bg-tertiary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.5rem',
                    color: 'var(--primary)',
                  }}
                >
                  <FaPlug />
                </div>

                <div style={{ flex: 1 }}>
                  <h3 style={{ marginBottom: '0.25rem' }}>{provider.display_name}</h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                    {provider.description}
                  </p>

                  <div style={{ display: 'flex', gap: '1rem', fontSize: '0.875rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {status.available ? (
                        <FaCheck style={{ color: 'var(--success)' }} />
                      ) : (
                        <FaTimes style={{ color: 'var(--danger)' }} />
                      )}
                      <span>Available</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {status.configured ? (
                        <FaCheck style={{ color: 'var(--success)' }} />
                      ) : (
                        <FaTimes style={{ color: 'var(--danger)' }} />
                      )}
                      <span>Configured</span>
                    </div>
                  </div>

                  {status.message && (
                    <p
                      style={{
                        marginTop: '0.75rem',
                        padding: '0.5rem',
                        background: 'var(--bg-primary)',
                        borderRadius: '0.25rem',
                        fontSize: '0.75rem',
                        color: status.available ? 'var(--success)' : 'var(--danger)',
                      }}
                    >
                      {status.message}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default Providers
