import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { FaPlus, FaTrash, FaSave, FaEye, FaCube } from 'react-icons/fa'
import { templateAPI, vagrantfileAPI, providerAPI } from '../services/api'
import './TemplateBuilder.css'

function TemplateBuilder() {
  const navigate = useNavigate()
  const [providers, setProviders] = useState([])
  const [templateName, setTemplateName] = useState('')
  const [templateDescription, setTemplateDescription] = useState('')
  const [selectedProvider, setSelectedProvider] = useState('virtualbox')
  const [blocks, setBlocks] = useState([])
  const [showPreview, setShowPreview] = useState(false)
  const [vagrantfilePreview, setVagrantfilePreview] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadProviders()
  }, [])

  const loadProviders = async () => {
    try {
      const response = await providerAPI.list()
      setProviders(response.data)
    } catch (error) {
      console.error('Failed to load providers:', error)
    }
  }

  const blockTypes = [
    {
      id: 'base',
      name: 'Base Configuration',
      icon: '📦',
      fields: [
        { name: 'box', label: 'Box Image', type: 'text', placeholder: 'bento/ubuntu-22.04' },
        { name: 'hostname', label: 'Hostname', type: 'text', placeholder: 'my-vm' },
      ]
    },
    {
      id: 'resources',
      name: 'Resources',
      icon: '⚙️',
      fields: [
        { name: 'cpus', label: 'CPUs', type: 'number', placeholder: '2', min: 1, max: 32 },
        { name: 'memory', label: 'Memory (MB)', type: 'number', placeholder: '2048', min: 512, step: 512 },
      ]
    },
    {
      id: 'network',
      name: 'Network',
      icon: '🌐',
      fields: [
        { name: 'type', label: 'Type', type: 'select', options: ['private_network', 'public_network', 'forwarded_port'] },
        { name: 'ip', label: 'IP Address', type: 'text', placeholder: '192.168.56.10', condition: (values) => values.type === 'private_network' },
        { name: 'guest_port', label: 'Guest Port', type: 'number', placeholder: '80', condition: (values) => values.type === 'forwarded_port' },
        { name: 'host_port', label: 'Host Port', type: 'number', placeholder: '8080', condition: (values) => values.type === 'forwarded_port' },
      ]
    },
    {
      id: 'storage',
      name: 'Storage',
      icon: '💾',
      fields: [
        { name: 'disk_size', label: 'Disk Size (MB)', type: 'number', placeholder: '32768' },
      ]
    },
    {
      id: 'synced_folder',
      name: 'Synced Folder',
      icon: '📁',
      fields: [
        { name: 'host_path', label: 'Host Path', type: 'text', placeholder: './data' },
        { name: 'guest_path', label: 'Guest Path', type: 'text', placeholder: '/vagrant/data' },
      ]
    },
    {
      id: 'provisioner',
      name: 'Shell Provisioner',
      icon: '🔧',
      fields: [
        { name: 'inline', label: 'Shell Commands (one per line)', type: 'textarea', placeholder: 'apt-get update\napt-get install -y nginx' },
      ]
    },
  ]

  const addBlock = (blockType) => {
    const newBlock = {
      id: Date.now(),
      type: blockType.id,
      name: blockType.name,
      icon: blockType.icon,
      values: {}
    }
    setBlocks([...blocks, newBlock])
  }

  const removeBlock = (blockId) => {
    setBlocks(blocks.filter(b => b.id !== blockId))
  }

  const updateBlockValue = (blockId, fieldName, value) => {
    setBlocks(blocks.map(block =>
      block.id === blockId
        ? { ...block, values: { ...block.values, [fieldName]: value } }
        : block
    ))
  }

  const generateVagrantfile = async () => {
    try {
      const config = buildConfig()
      const response = await vagrantfileAPI.generate(config)
      setVagrantfilePreview(response.data)
      setShowPreview(true)
    } catch (error) {
      console.error('Failed to generate Vagrantfile:', error)
      alert('Failed to generate Vagrantfile: ' + error.message)
    }
  }

  const buildConfig = () => {
    const config = {
      provider: selectedProvider,
      networks: [],
      synced_folders: [],
      provisioners: [],
      provider_config: {}
    }

    blocks.forEach(block => {
      switch (block.type) {
        case 'base':
          config.box = block.values.box
          config.hostname = block.values.hostname
          break
        case 'resources':
          config.cpus = parseInt(block.values.cpus) || 2
          config.memory = parseInt(block.values.memory) || 2048
          break
        case 'network':
          const network = { type: block.values.type }
          if (block.values.type === 'private_network') {
            network.ip = block.values.ip
          } else if (block.values.type === 'forwarded_port') {
            network.guest_port = parseInt(block.values.guest_port)
            network.host_port = parseInt(block.values.host_port)
          }
          config.networks.push(network)
          break
        case 'storage':
          config.disk_size = parseInt(block.values.disk_size)
          break
        case 'synced_folder':
          config.synced_folders.push({
            host_path: block.values.host_path,
            guest_path: block.values.guest_path
          })
          break
        case 'provisioner':
          if (block.values.inline) {
            config.provisioners.push({
              type: 'shell',
              inline: block.values.inline.split('\n').filter(line => line.trim())
            })
          }
          break
      }
    })

    return config
  }

  const saveTemplate = async () => {
    if (!templateName) {
      alert('Please enter a template name')
      return
    }

    setSaving(true)
    try {
      const config = buildConfig()

      const templateData = {
        name: templateName,
        description: templateDescription,
        provider: selectedProvider,
        config: config,
        tags: []
      }

      await templateAPI.create(templateData)
      alert('Template saved successfully!')
      navigate('/templates')
    } catch (error) {
      console.error('Failed to save template:', error)
      alert('Failed to save template: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  const renderBlockFields = (block) => {
    const blockType = blockTypes.find(bt => bt.id === block.type)
    if (!blockType) return null

    return blockType.fields.map(field => {
      // Check condition if exists
      if (field.condition && !field.condition(block.values)) {
        return null
      }

      return (
        <div key={field.name} className="block-field">
          <label>{field.label}</label>
          {field.type === 'select' ? (
            <select
              value={block.values[field.name] || ''}
              onChange={(e) => updateBlockValue(block.id, field.name, e.target.value)}
            >
              <option value="">Select...</option>
              {field.options.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          ) : field.type === 'textarea' ? (
            <textarea
              value={block.values[field.name] || ''}
              onChange={(e) => updateBlockValue(block.id, field.name, e.target.value)}
              placeholder={field.placeholder}
              rows={4}
            />
          ) : (
            <input
              type={field.type}
              value={block.values[field.name] || ''}
              onChange={(e) => updateBlockValue(block.id, field.name, e.target.value)}
              placeholder={field.placeholder}
              min={field.min}
              max={field.max}
              step={field.step}
            />
          )}
        </div>
      )
    })
  }

  return (
    <div className="template-builder">
      <div className="page-header">
        <div>
          <h1>Template Builder</h1>
          <p>Create VM templates using visual blocks</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={generateVagrantfile} className="btn btn-secondary">
            <FaEye /> Preview Vagrantfile
          </button>
          <button onClick={saveTemplate} disabled={saving} className="btn btn-primary">
            <FaSave /> {saving ? 'Saving...' : 'Save Template'}
          </button>
        </div>
      </div>

      <div className="builder-container">
        {/* Left Sidebar - Block Palette */}
        <div className="block-palette">
          <h3>Configuration Blocks</h3>
          <p className="palette-hint">Click to add blocks</p>

          {blockTypes.map(blockType => (
            <div
              key={blockType.id}
              className="palette-block"
              onClick={() => addBlock(blockType)}
            >
              <span className="block-icon">{blockType.icon}</span>
              <span className="block-name">{blockType.name}</span>
              <FaPlus className="add-icon" />
            </div>
          ))}
        </div>

        {/* Center - Canvas */}
        <div className="builder-canvas">
          <div className="template-info">
            <div className="form-group">
              <label>Template Name *</label>
              <input
                type="text"
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                placeholder="My Custom Template"
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <input
                type="text"
                value={templateDescription}
                onChange={(e) => setTemplateDescription(e.target.value)}
                placeholder="Describe your template..."
              />
            </div>

            <div className="form-group">
              <label>Provider *</label>
              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
              >
                {providers.map(p => (
                  <option key={p.name} value={p.name}>{p.display_name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="canvas-blocks">
            <h3>
              <FaCube /> Template Blocks {blocks.length > 0 && `(${blocks.length})`}
            </h3>

            {blocks.length === 0 ? (
              <div className="empty-canvas">
                <p>No blocks yet</p>
                <p className="empty-hint">Click blocks from the left sidebar to add them</p>
              </div>
            ) : (
              blocks.map((block, index) => (
                <div key={block.id} className="config-block">
                  <div className="block-header">
                    <span className="block-number">{index + 1}</span>
                    <span className="block-icon">{block.icon}</span>
                    <span className="block-title">{block.name}</span>
                    <button
                      onClick={() => removeBlock(block.id)}
                      className="btn-remove"
                      title="Remove block"
                    >
                      <FaTrash />
                    </button>
                  </div>
                  <div className="block-fields">
                    {renderBlockFields(block)}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <div className="preview-modal" onClick={() => setShowPreview(false)}>
          <div className="preview-content" onClick={(e) => e.stopPropagation()}>
            <div className="preview-header">
              <h2>Vagrantfile Preview</h2>
              <button onClick={() => setShowPreview(false)} className="btn-close">×</button>
            </div>
            <pre className="preview-code">{vagrantfilePreview}</pre>
            <div className="preview-actions">
              <button onClick={() => setShowPreview(false)} className="btn btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TemplateBuilder
