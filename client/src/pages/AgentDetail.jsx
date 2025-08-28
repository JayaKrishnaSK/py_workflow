import React from 'react'
import { useParams } from 'react-router-dom'

function AgentDetail() {
  const { id } = useParams()

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Agent Detail</h1>
      <p className="mt-2 text-sm text-gray-600">Agent ID: {id}</p>
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <p className="text-gray-500">Agent configuration and testing coming soon...</p>
      </div>
    </div>
  )
}

export default AgentDetail