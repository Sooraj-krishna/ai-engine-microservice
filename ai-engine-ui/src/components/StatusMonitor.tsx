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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
        <span className="ml-2 text-zinc-400 font-mono uppercase tracking-wider">Loading status...</span>
      </div>
    );
  }

  if (!systemStatus) {
    return (
      <div className="text-center py-8 text-zinc-500">
        <XCircle className="h-12 w-12 mx-auto mb-4 text-cyan-400" />
        <p className="font-bold uppercase tracking-wider">Unable to connect to AI Engine</p>
        <p className="text-sm">Make sure the service is running on port 8000</p>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return 'text-green-400 bg-green-950/50 border-green-800/50';
      case 'degraded': return 'text-yellow-400 bg-yellow-950/50 border-yellow-800/50';
      case 'unhealthy': return 'text-cyan-400 bg-cyan-950/50 border-cyan-800/50';
      default: return 'text-zinc-400 bg-zinc-900/50 border-zinc-800';
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
      <div className="dark-card rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-cyan-400 uppercase tracking-wider">System Health</h3>
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg border ${getStatusColor(systemStatus.health?.status)}`}>
            {getStatusIcon(systemStatus.health?.status)}
            <span className="font-bold uppercase tracking-wider text-xs">{systemStatus.health?.status || 'Unknown'}</span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-zinc-500">Version:</span>
            <span className="ml-2 font-bold text-white">{systemStatus.health?.version || 'N/A'}</span>
          </div>
          <div>
            <span className="text-zinc-500">Last Check:</span>
            <span className="ml-2 font-bold text-white">
              {systemStatus.health?.last_check ? 
                new Date(systemStatus.health.last_check).toLocaleTimeString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Environment Status */}
      <div className="dark-card rounded-lg p-4">
        <h3 className="text-lg font-bold text-cyan-400 mb-4 uppercase tracking-wider">Environment</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Globe className="h-4 w-4 text-zinc-500" />
              <span className="text-sm text-zinc-400">Website URL</span>
            </div>
            <span className={`text-xs px-2 py-1 rounded-lg font-bold uppercase tracking-wider ${
              systemStatus.environment?.website_url ? 'bg-green-950/50 text-green-400 border border-green-800/50' : 'bg-cyan-950/50 text-cyan-400 border border-cyan-800/50'
            }`}>
              {systemStatus.environment?.website_url ? 'Configured' : 'Not Set'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <GitBranch className="h-4 w-4 text-zinc-500" />
              <span className="text-sm text-zinc-400">GitHub Repo</span>
            </div>
            <span className={`text-xs px-2 py-1 rounded-lg font-bold uppercase tracking-wider ${
              systemStatus.environment?.github_repo ? 'bg-green-950/50 text-green-400 border border-green-800/50' : 'bg-cyan-950/50 text-cyan-400 border border-cyan-800/50'
            }`}>
              {systemStatus.environment?.github_repo ? 'Configured' : 'Not Set'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-4 w-4 text-zinc-500" />
              <span className="text-sm text-zinc-400">AI API</span>
            </div>
            <span className={`text-xs px-2 py-1 rounded-lg font-bold uppercase tracking-wider ${
              systemStatus.environment?.has_ai_api ? 'bg-green-950/50 text-green-400 border border-green-800/50' : 'bg-cyan-950/50 text-cyan-400 border border-cyan-800/50'
            }`}>
              {systemStatus.environment?.has_ai_api ? 'Connected' : 'Not Connected'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-zinc-500" />
              <span className="text-sm text-zinc-400">Improved Fixer</span>
            </div>
            <span className={`text-xs px-2 py-1 rounded-lg font-bold uppercase tracking-wider ${
              systemStatus.environment?.use_improved_fixer ? 'bg-purple-950/50 text-purple-400 border border-purple-800/50' : 'bg-zinc-900/50 text-zinc-400 border border-zinc-800'
            }`}>
              {systemStatus.environment?.use_improved_fixer ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-zinc-500" />
              <span className="text-sm text-zinc-400">Fix Testing</span>
            </div>
            <span className={`text-xs px-2 py-1 rounded-lg font-bold uppercase tracking-wider ${
              systemStatus.environment?.test_fixes_before_apply !== false ? 'bg-green-950/50 text-green-400 border border-green-800/50' : 'bg-cyan-950/50 text-cyan-400 border border-cyan-800/50'
            }`}>
              {systemStatus.environment?.test_fixes_before_apply !== false ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Brain className="h-4 w-4 text-zinc-500" />
              <span className="text-sm text-zinc-400">Code Analysis</span>
            </div>
            <span className={`text-xs px-2 py-1 rounded-lg font-bold uppercase tracking-wider ${
              systemStatus.environment?.code_analysis_enabled ? 'bg-purple-950/50 text-purple-400 border border-purple-800/50' : 'bg-zinc-900/50 text-zinc-400 border border-zinc-800'
            }`}>
              {systemStatus.environment?.code_analysis_enabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4">
        <h3 className="text-lg font-bold text-red-gradient mb-4 uppercase tracking-wide">Recent Activity</h3>
        <div className="space-y-3">
          {systemStatus.health?.last_run && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-zinc-500" />
                <span className="text-sm text-zinc-400">Last Run</span>
              </div>
              <span className="text-sm text-white">
                {new Date(systemStatus.health.last_run).toLocaleString()}
              </span>
            </div>
          )}
          
          {systemStatus.health?.last_pr && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <GitBranch className="h-4 w-4 text-zinc-500" />
                <span className="text-sm text-zinc-400">Last PR</span>
              </div>
              <a 
                href={systemStatus.health.last_pr} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-cyan-400 hover:text-cyan-400 hover:underline"
              >
                View PR
              </a>
            </div>
          )}
          
          {systemStatus.health?.last_error && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <XCircle className="h-4 w-4 text-cyan-400" />
                <span className="text-sm text-zinc-400">Last Error</span>
              </div>
              <span className="text-sm text-red-600 truncate max-w-xs">
                {systemStatus.health.last_error}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Safety Features */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4">
        <h3 className="text-lg font-bold text-red-gradient mb-4 uppercase tracking-wide">Safety Features</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm text-zinc-400">Validation</span>
            <span className={`text-xs px-2 py-1 rounded-lg font-bold uppercase tracking-wider ${
              systemStatus.health?.safety_features?.validation_enabled ? 'bg-green-950/50 text-green-400 border border-green-800/50' : 'bg-cyan-950/50 text-cyan-400 border border-cyan-800/50'
            }`}>
              {systemStatus.health?.safety_features?.validation_enabled ? 'ON' : 'OFF'}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm text-zinc-400">Rollback</span>
            <span className={`text-xs px-2 py-1 rounded-lg font-bold uppercase tracking-wider ${
              systemStatus.health?.safety_features?.rollback_enabled ? 'bg-green-950/50 text-green-400 border border-green-800/50' : 'bg-cyan-950/50 text-cyan-400 border border-cyan-800/50'
            }`}>
              {systemStatus.health?.safety_features?.rollback_enabled ? 'ON' : 'OFF'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
