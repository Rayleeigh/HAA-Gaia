import { useState, useEffect } from 'react'
import { FaLayerGroup, FaDownload } from 'react-icons/fa'
import { templateAPI } from '../services/api'

function Templates() {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const response = await templateAPI.list()
      setTemplates(response.data)
    } catch (error) {
      console.error('Failed to load templates:', error)
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
        <h1>Templates</h1>
        <p>Reusable VM configuration templates</p>
      </div>

      {templates.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <FaLayerGroup style={{ fontSize: '3rem', color: 'var(--text-secondary)', marginBottom: '1rem' }} />
          <p style={{ color: 'var(--text-secondary)' }}>No templates yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-3">
          {templates.map((template) => (
            <div key={template.id} className="card">
              <h3 style={{ marginBottom: '0.5rem' }}>{template.name}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1rem' }}>
                {template.description || 'No description'}
              </p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  {template.provider}
                </span>
                <button className="btn btn-primary btn-sm">
                  <FaDownload /> Use Template
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Templates
