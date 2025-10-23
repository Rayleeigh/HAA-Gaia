import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FaPlay, FaStop, FaTrash, FaPlus } from 'react-icons/fa'
import { vmAPI } from '../services/api'
import './VMList.css'

function VMList() {
  const [vms, setVMs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadVMs()
  }, [])

  const loadVMs = async () => {
    try {
      const response = await vmAPI.list()
      setVMs(response.data)
    } catch (error) {
      console.error('Failed to load VMs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async (id) => {
    try {
      await vmAPI.start(id)
      loadVMs()
    } catch (error) {
      console.error('Failed to start VM:', error)
    }
  }

  const handleStop = async (id) => {
    try {
      await vmAPI.stop(id)
      loadVMs()
    } catch (error) {
      console.error('Failed to stop VM:', error)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this VM?')) return

    try {
      await vmAPI.delete(id)
      loadVMs()
    } catch (error) {
      console.error('Failed to delete VM:', error)
    }
  }

  const getStateColor = (state) => {
    const colors = {
      running: 'green',
      stopped: 'red',
      creating: 'blue',
      error: 'red',
    }
    return colors[state] || 'gray'
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="vm-list">
      <div className="page-header">
        <div>
          <h1>Virtual Machines</h1>
          <p>Manage your virtual machines</p>
        </div>
        <Link to="/vms/create" className="btn btn-primary">
          <FaPlus /> Create VM
        </Link>
      </div>

      {vms.length === 0 ? (
        <div className="empty-state">
          <p>No virtual machines yet</p>
          <Link to="/vms/create" className="btn btn-primary">
            Create Your First VM
          </Link>
        </div>
      ) : (
        <div className="vm-grid">
          {vms.map((vm) => (
            <div key={vm.id} className="vm-card">
              <div className="vm-header">
                <h3>{vm.name}</h3>
                <span className={`state-badge state-${getStateColor(vm.state)}`}>
                  {vm.state}
                </span>
              </div>

              <div className="vm-details">
                <div className="detail-row">
                  <span className="label">Provider:</span>
                  <span className="value">{vm.provider}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Created:</span>
                  <span className="value">
                    {new Date(vm.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="vm-actions">
                {vm.state === 'stopped' && (
                  <button
                    onClick={() => handleStart(vm.id)}
                    className="btn btn-success"
                    title="Start VM"
                  >
                    <FaPlay />
                  </button>
                )}
                {vm.state === 'running' && (
                  <button
                    onClick={() => handleStop(vm.id)}
                    className="btn btn-secondary"
                    title="Stop VM"
                  >
                    <FaStop />
                  </button>
                )}
                <button
                  onClick={() => handleDelete(vm.id)}
                  className="btn btn-danger"
                  title="Delete VM"
                >
                  <FaTrash />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default VMList
