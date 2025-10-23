import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { vmAPI, templateAPI, providerAPI } from '../services/api'
import './CreateVM.css'

function CreateVM() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [providers, setProviders] = useState([])
  const [templates, setTemplates] = useState([])

  const [formData, setFormData] = useState({
    name: '',
    provider: 'proxmox',
    template_id: null,
    description: '',
    config: {
      box: 'generic/ubuntu2204',
      cpus: 2,
      memory: 2048,
      provider_config: {
        node: 'pve',
        storage: 'local-lvm',
        disk_size: '32G',
      },
    },
  })

  useEffect(() => {
    loadProviders()
    loadTemplates()
  }, [])

  const loadProviders = async () => {
    try {
      const response = await providerAPI.list()
      setProviders(response.data)
    } catch (error) {
      console.error('Failed to load providers:', error)
    }
  }

  const loadTemplates = async () => {
    try {
      const response = await templateAPI.list()
      setTemplates(response.data)
    } catch (error) {
      console.error('Failed to load templates:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await vmAPI.create(formData)
      navigate('/vms')
    } catch (error) {
      console.error('Failed to create VM:', error)
      alert('Failed to create VM: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const updateConfig = (key, value) => {
    setFormData({
      ...formData,
      config: {
        ...formData.config,
        [key]: value,
      },
    })
  }

  const updateProviderConfig = (key, value) => {
    setFormData({
      ...formData,
      config: {
        ...formData.config,
        provider_config: {
          ...formData.config.provider_config,
          [key]: value,
        },
      },
    })
  }

  return (
    <div className="create-vm">
      <div className="page-header">
        <h1>Create Virtual Machine</h1>
        <p>Configure and deploy a new virtual machine</p>
      </div>

      <form onSubmit={handleSubmit} className="vm-form">
        <div className="form-section">
          <h2>Basic Information</h2>

          <div className="form-group">
            <label htmlFor="name">VM Name *</label>
            <input
              type="text"
              id="name"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="my-vm"
            />
          </div>

          <div className="form-group">
            <label htmlFor="provider">Provider *</label>
            <select
              id="provider"
              required
              value={formData.provider}
              onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
            >
              {providers.map((p) => (
                <option key={p.name} value={p.name}>
                  {p.display_name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Description of this VM"
              rows={3}
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Resources</h2>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="cpus">CPUs</label>
              <input
                type="number"
                id="cpus"
                min="1"
                max="32"
                value={formData.config.cpus}
                onChange={(e) => updateConfig('cpus', parseInt(e.target.value))}
              />
            </div>

            <div className="form-group">
              <label htmlFor="memory">Memory (MB)</label>
              <input
                type="number"
                id="memory"
                min="512"
                step="512"
                value={formData.config.memory}
                onChange={(e) => updateConfig('memory', parseInt(e.target.value))}
              />
            </div>
          </div>
        </div>

        {formData.provider === 'proxmox' && (
          <div className="form-section">
            <h2>Proxmox Configuration</h2>

            <div className="form-group">
              <label htmlFor="node">Node</label>
              <input
                type="text"
                id="node"
                value={formData.config.provider_config.node}
                onChange={(e) => updateProviderConfig('node', e.target.value)}
                placeholder="pve"
              />
            </div>

            <div className="form-group">
              <label htmlFor="storage">Storage</label>
              <input
                type="text"
                id="storage"
                value={formData.config.provider_config.storage}
                onChange={(e) => updateProviderConfig('storage', e.target.value)}
                placeholder="local-lvm"
              />
            </div>

            <div className="form-group">
              <label htmlFor="disk_size">Disk Size</label>
              <input
                type="text"
                id="disk_size"
                value={formData.config.provider_config.disk_size}
                onChange={(e) => updateProviderConfig('disk_size', e.target.value)}
                placeholder="32G"
              />
            </div>
          </div>
        )}

        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate('/vms')}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Creating...' : 'Create VM'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default CreateVM
