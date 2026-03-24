'use client';

import { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, AlertTriangle, Clock, GitBranch, Globe, Brain } from 'lucide-react';

interface StatusMonitorProps {
  status: any;
}

export function StatusMonitor({ status }: StatusMonitorProps) {
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    if (status) {
      setLastUpdated(new Date());
    }
  }, [status]);

  if (!status) {
    return (
      <div className="flex items-center justify-center p-8 bg-white/5 border border-white/10 rounded-lg animate-pulse">
        <Activity className="h-6 w-6 text-white/40 mr-2" />
        <span className="text-white/40 font-mono uppercase tracking-wider text-sm">Waiting for system status...</span>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'active': // Added active
      case 'connected': // Added connected
        return 'text-green-400';
      case 'degraded':
      case 'warning':
        return 'text-yellow-400';
      case 'down':
      case 'error':
      case 'disconnected':
        return 'text-red-400';
      default:
        return 'text-white/40';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'active':
      case 'connected':
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'degraded':
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
      case 'down':
      case 'error':
      case 'disconnected':
        return <XCircle className="h-5 w-5 text-red-400" />;
      default:
        return <Activity className="h-5 w-5 text-white/40" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* System Health Header */}
      <div className="bg-white/5 border border-white/10 rounded-lg p-5 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className={`absolute inset-0 rounded-full blur-md opacity-50 ${status.system_status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <div className={`relative bg-black rounded-full p-2 border ${status.system_status === 'healthy' ? 'border-green-500/50' : 'border-red-500/50'}`}>
              <Activity className={`h-6 w-6 ${getStatusColor(status.system_status)}`} />
            </div>
          </div>
          <div>
            <h3 className="text-white font-bold text-lg uppercase tracking-wide">System Health</h3>
            <p className="text-white/40 text-xs font-mono mt-1">
              LAST UPDATE: {lastUpdated.toLocaleTimeString()}
            </p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full border ${status.system_status === 'healthy' ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'} flex items-center gap-2`}>
          <div className={`w-2 h-2 rounded-full ${status.system_status === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
          <span className={`text-xs font-bold uppercase tracking-wider ${getStatusColor(status.system_status)}`}>
            {status.system_status || 'UNKNOWN'}
          </span>
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* GitHub API */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-4 group hover:bg-white/[0.08] transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white/5 rounded-lg group-hover:bg-white/10 transition-colors">
                <GitBranch className="h-5 w-5 text-white/80" />
              </div>
              <span className="text-white/80 font-medium">GitHub API</span>
            </div>
            {getStatusIcon(status.services?.github)}
          </div>
          <div className="flex items-center justify-between pl-12">
            <span className="text-xs text-white/40 uppercase tracking-wider font-bold">Status</span>
            <span className={`text-xs font-bold uppercase tracking-wider ${getStatusColor(status.services?.github)}`}>
              {status.services?.github || 'UNKNOWN'}
            </span>
          </div>
        </div>

        {/* Database */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-4 group hover:bg-white/[0.08] transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white/5 rounded-lg group-hover:bg-white/10 transition-colors">
                <Clock className="h-5 w-5 text-white/80" />
              </div>
              <span className="text-white/80 font-medium">Database</span>
            </div>
            {getStatusIcon(status.services?.database)}
          </div>
          <div className="flex items-center justify-between pl-12">
            <span className="text-xs text-white/40 uppercase tracking-wider font-bold">Status</span>
            <span className={`text-xs font-bold uppercase tracking-wider ${getStatusColor(status.services?.database)}`}>
              {status.services?.database || 'UNKNOWN'}
            </span>
          </div>
        </div>

        {/* AI Engine */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-4 group hover:bg-white/[0.08] transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white/5 rounded-lg group-hover:bg-white/10 transition-colors">
                <Brain className="h-5 w-5 text-white/80" />
              </div>
              <span className="text-white/80 font-medium">AI Engine</span>
            </div>
             {getStatusIcon(status.services?.ai_engine || 'connected')}
          </div>
           <div className="flex items-center justify-between pl-12">
            <span className="text-xs text-white/40 uppercase tracking-wider font-bold">Status</span>
            <span className={`text-xs font-bold uppercase tracking-wider ${getStatusColor(status.services?.ai_engine || 'connected')}`}>
              {status.services?.ai_engine || 'CONNECTED'}
            </span>
          </div>
        </div>

        {/* Web Server */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-4 group hover:bg-white/[0.08] transition-all">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white/5 rounded-lg group-hover:bg-white/10 transition-colors">
                <Globe className="h-5 w-5 text-white/80" />
              </div>
              <span className="text-white/80 font-medium">Web Server</span>
            </div>
            {getStatusIcon('active')}
          </div>
           <div className="flex items-center justify-between pl-12">
            <span className="text-xs text-white/40 uppercase tracking-wider font-bold">Status</span>
            <span className="text-xs font-bold uppercase tracking-wider text-green-400">
              ACTIVE
            </span>
          </div>
        </div>
      </div>
      
      {/* Current Task - optional display if needed */}
      {status.current_task && (
         <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-center justify-between">
            <span className="text-xs text-blue-300 font-bold uppercase tracking-wide">Processing</span>
            <span className="text-xs text-blue-200">{status.current_task}</span>
         </div>
      )}
    </div>
  );
}
