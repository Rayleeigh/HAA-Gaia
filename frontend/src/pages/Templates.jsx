import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FaLayerGroup, FaDownload, FaPlus } from 'react-icons/fa'
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
      <div className="page-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <h1>Templates</h1>
          <p>Reusable VM configuration templates</p>
        </div>

        {/* Create New Template button */}
        <Link to="/templates/builder" className="btn btn-primary">
          <FaPlus style={{ marginRight: '0.5rem' }} />
          Create new template
        </Link>
      </div>

      {templates.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <FaLayerGroup style={{ fontSize: '3rem', color: 'var(--text-secondary)', marginBottom: '1rem' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>No templates yet</p>

          {/* Empty state CTA */}
          <Link to="/templates/builder" className="btn btn-primary">
            <FaPlus style={{ marginRight: '0.5rem' }} />
            Create your first template
          </Link>
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
