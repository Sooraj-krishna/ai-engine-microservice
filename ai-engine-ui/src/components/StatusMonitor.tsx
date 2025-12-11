'use client';

import { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, AlertTriangle, Clock, GitBranch, Globe, Brain } from 'lucide-react';


interface StatusMonitorProps {
  status: any;
}

export function StatusMonitor({ status }: StatusMonitorProps) {
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/status');
        if (response.ok) {
          const data = await response.json();
          setSystemStatus(data);
        }
      } catch (error) {
        console.error('Failed to fetch status:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading status...</span>
      </div>
    );
  }

  if (!systemStatus) {
    return (
      <div className="text-center py-8 text-gray-500">
        <XCircle className="h-12 w-12 mx-auto mb-4 text-red-500" />
        <p>Unable to connect to AI Engine</p>
        <p className="text-sm">Make sure the service is running on port 8000</p>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return 'text-green-600 bg-green-50';
      case 'degraded': return 'text-yellow-600 bg-yellow-50';
      case 'unhealthy': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return <CheckCircle className="h-5 w-5" />;
      case 'degraded': return <AlertTriangle className="h-5 w-5" />;
      case 'unhealthy': return <XCircle className="h-5 w-5" />;
      default: return <Activity className="h-5 w-5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">System Health</h3>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${getStatusColor(systemStatus.health?.status)}`}>
            {getStatusIcon(systemStatus.health?.status)}
            <span className="font-medium">{systemStatus.health?.status || 'Unknown'}</span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Version:</span>
            <span className="ml-2 font-medium">{systemStatus.health?.version || 'N/A'}</span>
          </div>
          <div>
            <span className="text-gray-600">Last Check:</span>
            <span className="ml-2 font-medium">
              {systemStatus.health?.last_check ? 
                new Date(systemStatus.health.last_check).toLocaleTimeString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Environment Status */}
      <div className="bg-white border rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Environment</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Globe className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Website URL</span>
            </div>
            <span className={`text-sm px-2 py-1 rounded ${
              systemStatus.environment?.website_url ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {systemStatus.environment?.website_url ? 'Configured' : 'Not Set'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <GitBranch className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">GitHub Repo</span>
            </div>
            <span className={`text-sm px-2 py-1 rounded ${
              systemStatus.environment?.github_repo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {systemStatus.environment?.github_repo ? 'Configured' : 'Not Set'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">AI API</span>
            </div>
            <span className={`text-sm px-2 py-1 rounded ${
              systemStatus.environment?.has_openrouter_token ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {systemStatus.environment?.has_openrouter_token ? 'Connected' : 'Not Connected'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Improved Fixer</span>
            </div>
            <span className={`text-sm px-2 py-1 rounded ${
              systemStatus.environment?.use_improved_fixer ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
            }`}>
              {systemStatus.environment?.use_improved_fixer ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Fix Testing</span>
            </div>
            <span className={`text-sm px-2 py-1 rounded ${
              systemStatus.environment?.test_fixes_before_apply !== false ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {systemStatus.environment?.test_fixes_before_apply !== false ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Code Analysis</span>
            </div>
            <span className={`text-sm px-2 py-1 rounded ${
              systemStatus.environment?.code_analysis_enabled ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
            }`}>
              {systemStatus.environment?.code_analysis_enabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white border rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {systemStatus.health?.last_run && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">Last Run</span>
              </div>
              <span className="text-sm text-gray-800">
                {new Date(systemStatus.health.last_run).toLocaleString()}
              </span>
            </div>
          )}
          
          {systemStatus.health?.last_pr && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <GitBranch className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">Last PR</span>
              </div>
              <a 
                href={systemStatus.health.last_pr} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline"
              >
                View PR
              </a>
            </div>
          )}
          
          {systemStatus.health?.last_error && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <XCircle className="h-4 w-4 text-red-500" />
                <span className="text-sm text-gray-600">Last Error</span>
              </div>
              <span className="text-sm text-red-600 truncate max-w-xs">
                {systemStatus.health.last_error}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Safety Features */}
      <div className="bg-white border rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Safety Features</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm text-gray-600">Validation</span>
            <span className={`text-xs px-2 py-1 rounded ${
              systemStatus.health?.safety_features?.validation_enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {systemStatus.health?.safety_features?.validation_enabled ? 'ON' : 'OFF'}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm text-gray-600">Rollback</span>
            <span className={`text-xs px-2 py-1 rounded ${
              systemStatus.health?.safety_features?.rollback_enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {systemStatus.health?.safety_features?.rollback_enabled ? 'ON' : 'OFF'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
