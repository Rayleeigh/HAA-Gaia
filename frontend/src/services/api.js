import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Virtual Machines
export const vmAPI = {
  list: (params) => api.get('/vms', { params }),
  get: (id) => api.get(`/vms/${id}`),
  create: (data) => api.post('/vms', data),
  start: (id) => api.post(`/vms/${id}/start`),
  stop: (id) => api.post(`/vms/${id}/stop`),
  delete: (id) => api.delete(`/vms/${id}`),
  getStatus: (id) => api.get(`/vms/${id}/status`),
}

// Templates
export const templateAPI = {
  list: (params) => api.get('/templates', { params }),
  get: (id) => api.get(`/templates/${id}`),
  create: (data) => api.post('/templates', data),
  update: (id, data) => api.put(`/templates/${id}`, data),
  delete: (id) => api.delete(`/templates/${id}`),
  import: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/templates/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// Vagrantfiles
export const vagrantfileAPI = {
  generate: (config) => api.post('/vagrantfiles/generate', config),
  parse: (vagrantfile) => api.post('/vagrantfiles/parse', { vagrantfile }),
  validate: (vagrantfile) => api.post('/vagrantfiles/validate', { vagrantfile }),
}

// Providers
export const providerAPI = {
  list: () => api.get('/providers'),
  get: (name) => api.get(`/providers/${name}`),
  getStatus: (name) => api.get(`/providers/${name}/status`),
  getCapabilities: (name) => api.get(`/providers/${name}/capabilities`),
}

export default api
