import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  DocumentTextIcon,
  PlayIcon,
  UserGroupIcon,
  WrenchIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import { workflowsApi, executionsApi, agentsApi, toolsApi, healthApi } from '../services/api'

function Dashboard() {
  const [stats, setStats] = useState({
    workflows: 0,
    executions: 0,
    agents: 0,
    tools: 0,
  })
  const [recentExecutions, setRecentExecutions] = useState([])
  const [healthStatus, setHealthStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch statistics
      const [workflowsRes, executionsRes, agentsRes, toolsRes, healthRes] = await Promise.all([
        workflowsApi.getAll({ limit: 1 }),
        executionsApi.getAll({ limit: 10 }),
        agentsApi.getAll({ limit: 1 }),
        toolsApi.getAll(),
        healthApi.checkDetailedHealth(),
      ])

      setStats({
        workflows: workflowsRes.data.length,
        executions: executionsRes.data.length,
        agents: agentsRes.data.length,
        tools: toolsRes.data.count || 0,
      })

      setRecentExecutions(executionsRes.data.slice(0, 5))
      setHealthStatus(healthRes.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'failed':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
      case 'running':
        return <ClockIcon className="h-5 w-5 text-blue-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusBadge = (status) => {
    const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    switch (status) {
      case 'completed':
        return `${baseClasses} status-completed`
      case 'failed':
        return `${baseClasses} status-failed`
      case 'running':
        return `${baseClasses} status-running`
      case 'paused':
        return `${baseClasses} status-paused`
      default:
        return `${baseClasses} status-draft`
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow h-32" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-sm text-gray-600">
          Overview of your agentic workflow system
        </p>
      </div>

      {/* Health Status */}
      {healthStatus && (
        <div className={`rounded-md p-4 ${
          healthStatus.status === 'healthy' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex">
            {healthStatus.status === 'healthy' ? (
              <CheckCircleIcon className="h-5 w-5 text-green-400" />
            ) : (
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            )}
            <div className="ml-3">
              <h3 className={`text-sm font-medium ${
                healthStatus.status === 'healthy' ? 'text-green-800' : 'text-red-800'
              }`}>
                System Status: {healthStatus.status}
              </h3>
              <div className="mt-2 text-sm text-gray-600">
                <p>Database: {healthStatus.components?.database?.status || 'unknown'}</p>
                <p>Default LLM Provider: {healthStatus.components?.llm_providers?.default || 'unknown'}</p>
                <p>Tracing: {healthStatus.components?.tracing?.enabled ? 'enabled' : 'disabled'}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Workflows</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.workflows}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <Link to="/workflows" className="font-medium text-blue-700 hover:text-blue-900">
                View all workflows
              </Link>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <PlayIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Executions</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.executions}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <Link to="/executions" className="font-medium text-blue-700 hover:text-blue-900">
                View all executions
              </Link>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Agents</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.agents}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <Link to="/agents" className="font-medium text-blue-700 hover:text-blue-900">
                View all agents
              </Link>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <WrenchIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Tools</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.tools}</dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-5 py-3">
            <div className="text-sm">
              <Link to="/tools" className="font-medium text-blue-700 hover:text-blue-900">
                View all tools
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Executions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Executions</h3>
          <div className="mt-6 flow-root">
            {recentExecutions.length > 0 ? (
              <ul className="-my-5 divide-y divide-gray-200">
                {recentExecutions.map((execution) => (
                  <li key={execution.id} className="py-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        {getStatusIcon(execution.status)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          Execution {execution.id.slice(-8)}
                        </p>
                        <p className="text-sm text-gray-500">
                          Workflow: {execution.workflow_id}
                        </p>
                      </div>
                      <div className="flex-shrink-0">
                        <span className={getStatusBadge(execution.status)}>
                          {execution.status}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No executions yet</p>
            )}
          </div>
          <div className="mt-6">
            <Link
              to="/executions"
              className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              View all
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard