import { useState, useEffect } from 'react'
import { FaSave, FaCheck, FaTimes } from 'react-icons/fa'
import { providerAPI } from '../services/api'
import './ProviderSettings.css'

function ProviderSettings() {
  const [providers, setProviders] = useState([])
  const [selectedProvider, setSelectedProvider] = useState(null)
  const [config, setConfig] = useState({})
  const [testResult, setTestResult] = useState(null)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)

  useEffect(() => {
    loadProviders()
  }, [])

  // Load saved config when provider changes
  useEffect(() => {
    if (selectedProvider) {
      loadSavedConfig(selectedProvider)
      setTestResult(null) // Clear previous test results
    }
  }, [selectedProvider])

  const loadProviders = async () => {
    try {
      const response = await providerAPI.list()
      setProviders(response.data)
      if (response.data.length > 0) {
        setSelectedProvider(response.data[0].name)
      }
    } catch (error) {
      console.error('Failed to load providers:', error)
    }
  }

  const loadSavedConfig = (providerName) => {
    try {
      const savedConfig = localStorage.getItem(`provider_config_${providerName}`)
      if (savedConfig) {
        setConfig(JSON.parse(savedConfig))
      } else {
        setConfig({}) // Reset config if no saved data
      }
    } catch (error) {
      console.error('Failed to load saved config:', error)
      setConfig({})
    }
  }

  const testConnection = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const response = await providerAPI.getStatus(selectedProvider)
      setTestResult(response.data)
    } catch (error) {
      setTestResult({
        available: false,
        configured: false,
        message: 'Connection test failed: ' + error.message
      })
    } finally {
      setTesting(false)
    }
  }

  const saveConfig = async () => {
    setSaving(true)
    try {
      // Save to localStorage for now (in production, save to backend)
      localStorage.setItem(`provider_config_${selectedProvider}`, JSON.stringify(config))
      alert('Configuration saved!')
    } catch (error) {
      alert('Failed to save configuration: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  const renderConfigForm = () => {
    if (!selectedProvider) return null

    switch (selectedProvider) {
      case 'proxmox':
        return (
          <div className="config-form">
            <div className="form-group">
              <label>Proxmox Host</label>
              <input
                type="text"
                value={config.host || ''}
                onChange={(e) => setConfig({ ...config, host: e.target.value })}
                placeholder="proxmox.example.com"
              />
            </div>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={config.user || 'root@pam'}
                onChange={(e) => setConfig({ ...config, user: e.target.value })}
                placeholder="root@pam"
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={config.password || ''}
                onChange={(e) => setConfig({ ...config, password: e.target.value })}
                placeholder="Enter password"
              />
            </div>
            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={!config.verify_ssl}
                  onChange={(e) => setConfig({ ...config, verify_ssl: !e.target.checked })}
                />
                {' '}Skip SSL verification (self-signed certificates)
              </label>
            </div>
          </div>
        )

      case 'virtualbox':
        return (
          <div className="config-form">
            <div className="info-box">
              <p>VirtualBox is managed through VBoxManage CLI.</p>
              <p>Ensure VirtualBox is installed and VBoxManage is in your PATH.</p>
            </div>
            <div className="form-group">
              <label>Default VM Location</label>
              <input
                type="text"
                value={config.vm_folder || ''}
                onChange={(e) => setConfig({ ...config, vm_folder: e.target.value })}
                placeholder="C:\Users\YourName\VirtualBox VMs"
              />
            </div>
          </div>
        )

      case 'hyperv':
        return (
          <div className="config-form">
            <div className="info-box">
              <p>Hyper-V requires Windows 10 Pro/Enterprise or Windows Server.</p>
              <p>Run PowerShell as Administrator to enable:</p>
              <code>Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All</code>
            </div>
            <div className="form-group">
              <label>Default Virtual Hard Disk Path</label>
              <input
                type="text"
                value={config.vhd_path || ''}
                onChange={(e) => setConfig({ ...config, vhd_path: e.target.value })}
                placeholder="C:\Users\Public\Documents\Hyper-V\Virtual Hard Disks"
              />
            </div>
            <div className="form-group">
              <label>Default Virtual Switch</label>
              <input
                type="text"
                value={config.switch_name || ''}
                onChange={(e) => setConfig({ ...config, switch_name: e.target.value })}
                placeholder="Default Switch"
              />
            </div>
          </div>
        )

      case 'wsl':
        return (
          <div className="config-form">
            <div className="info-box">
              <p>WSL2 requires Windows 10 version 2004+ or Windows 11.</p>
              <p>Install WSL with: <code>wsl --install</code></p>
            </div>
            <div className="form-group">
              <label>Default Install Location</label>
              <input
                type="text"
                value={config.install_path || ''}
                onChange={(e) => setConfig({ ...config, install_path: e.target.value })}
                placeholder="C:\WSL"
              />
            </div>
            <div className="form-group">
              <label>Default Distribution</label>
              <input
                type="text"
                value={config.default_distro || ''}
                onChange={(e) => setConfig({ ...config, default_distro: e.target.value })}
                placeholder="Ubuntu-22.04"
              />
            </div>
          </div>
        )

      default:
        return <p>No configuration needed for this provider.</p>
    }
  }

  return (
    <div className="provider-settings">
      <div className="page-header">
        <h1>Provider Configuration</h1>
        <p>Configure virtualization provider connections</p>
      </div>

      <div className="settings-container">
        <div className="provider-list">
          <h3>Select Provider</h3>
          {providers.length === 0 ? (
            <p className="no-providers">Loading providers...</p>
          ) : (
            providers.map((provider) => (
              <div
                key={provider.name}
                className={`provider-item ${selectedProvider === provider.name ? 'active' : ''}`}
                onClick={() => setSelectedProvider(provider.name)}
              >
                <div className="provider-name">{provider.display_name}</div>
                <div className="provider-type">{provider.name}</div>
              </div>
            ))
          )}
        </div>

        <div className="provider-config">
          {selectedProvider && (
            <>
              <h2>{providers.find(p => p.name === selectedProvider)?.display_name} Configuration</h2>

              {renderConfigForm()}

              <div className="config-actions">
                <button
                  onClick={testConnection}
                  disabled={testing}
                  className="btn btn-secondary"
                >
                  {testing ? 'Testing...' : 'Test Connection'}
                </button>
                <button
                  onClick={saveConfig}
                  disabled={saving}
                  className="btn btn-primary"
                >
                  <FaSave /> {saving ? 'Saving...' : 'Save Configuration'}
                </button>
              </div>

              {testResult && (
                <div className={`test-result ${testResult.available ? 'success' : 'error'}`}>
                  <div className="result-icon">
                    {testResult.available ? <FaCheck /> : <FaTimes />}
                  </div>
                  <div className="result-content">
                    <div className="result-status">
                      {testResult.available ? 'Connection Successful' : 'Connection Failed'}
                    </div>
                    <div className="result-message">{testResult.message}</div>
                    {testResult.version && (
                      <div className="result-version">Version: {testResult.version}</div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProviderSettings
