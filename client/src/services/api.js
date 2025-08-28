import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Health API
export const healthApi = {
  checkHealth: () => api.get('/health/'),
  checkDetailedHealth: () => api.get('/health/detailed'),
}

// Workflows API
export const workflowsApi = {
  create: (data) => api.post('/workflows/', data),
  getAll: (params = {}) => api.get('/workflows/', { params }),
  getById: (id) => api.get(`/workflows/${id}`),
  update: (id, data) => api.put(`/workflows/${id}`, data),
  delete: (id) => api.delete(`/workflows/${id}`),
  duplicate: (id, newName) => api.post(`/workflows/${id}/duplicate`, null, { params: { new_name: newName } }),
  validate: (id) => api.post(`/workflows/${id}/validate`),
  test: (id, testInput) => api.post(`/workflows/${id}/test`, testInput),
}

// Executions API
export const executionsApi = {
  create: (data) => api.post('/executions/', data),
  start: (id) => api.post(`/executions/${id}/start`),
  getAll: (params = {}) => api.get('/executions/', { params }),
  getById: (id) => api.get(`/executions/${id}`),
  cancel: (id) => api.post(`/executions/${id}/cancel`),
  getInteractions: (id) => api.get(`/executions/${id}/interactions`),
  respondToInteraction: (executionId, interactionId, response) => 
    api.post(`/executions/${executionId}/interactions/${interactionId}/respond`, { response }),
  getLogs: (id) => api.get(`/executions/${id}/logs`),
  getStatus: (id) => api.get(`/executions/${id}/status`),
}

// Agents API
export const agentsApi = {
  create: (data) => api.post('/agents/', data),
  getAll: (params = {}) => api.get('/agents/', { params }),
  getById: (id) => api.get(`/agents/${id}`),
  update: (id, data) => api.put(`/agents/${id}`, data),
  delete: (id) => api.delete(`/agents/${id}`),
  test: (id, testInput) => api.post(`/agents/${id}/test`, null, { params: { test_input: testInput } }),
  getTypes: () => api.get('/agents/types/'),
}

// Tools API
export const toolsApi = {
  getAll: () => api.get('/tools/'),
  getById: (name) => api.get(`/tools/${name}`),
  getProviders: () => api.get('/tools/providers/'),
  getProviderModels: (provider) => api.get(`/tools/providers/${provider}/models`),
}

export default api