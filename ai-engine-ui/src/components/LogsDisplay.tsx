'use client';

import { useState, useEffect, useRef } from 'react';
import { Terminal, Download, Trash2, RefreshCw } from 'lucide-react';

interface LogsDisplayProps {
  logs: string[];
}

export function LogsDisplay({ logs }: LogsDisplayProps) {
  const [isAutoScroll, setIsAutoScroll] = useState(true);
  const [filter, setFilter] = useState('all');
  const logsEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isAutoScroll) {
      scrollToBottom();
    }
  }, [logs, isAutoScroll]);

  const filteredLogs = logs.filter(log => {
    if (filter === 'all') return true;
    if (filter === 'info') return log.includes('[INFO]');
    if (filter === 'success') return log.includes('[SUCCESS]');
    if (filter === 'error') return log.includes('[ERROR]');
    if (filter === 'warning') return log.includes('[WARNING]');
    if (filter === 'debug') return log.includes('[DEBUG]');
    return true;
  });

  const getLogLevel = (log: string) => {
    if (log.includes('[ERROR]')) return 'error';
    if (log.includes('[WARNING]')) return 'warning';
    if (log.includes('[SUCCESS]')) return 'success';
    if (log.includes('[DEBUG]')) return 'debug';
    if (log.includes('[INFO]')) return 'info';
    return 'default';
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-600 bg-red-50';
      case 'warning': return 'text-yellow-600 bg-yellow-50';
      case 'success': return 'text-green-600 bg-green-50';
      case 'debug': return 'text-blue-600 bg-blue-50';
      case 'info': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-800 bg-white';
    }
  };

  const downloadLogs = () => {
    const logContent = logs.join('\n');
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-engine-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const clearLogs = () => {
    // This would need to be implemented in the parent component
    // For now, we'll just show a message
    alert('Logs cleared! (This would clear logs in a real implementation)');
  };

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Terminal className="h-5 w-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">
              Logs ({filteredLogs.length})
            </span>
          </div>
          
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Logs</option>
            <option value="info">Info</option>
            <option value="success">Success</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="debug">Debug</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsAutoScroll(!isAutoScroll)}
            className={`px-3 py-1 text-sm rounded-md ${
              isAutoScroll 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-gray-100 text-gray-700'
            }`}
          >
            Auto-scroll {isAutoScroll ? 'ON' : 'OFF'}
          </button>
          
          <button
            onClick={downloadLogs}
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            <Download className="h-4 w-4" />
            <span>Download</span>
          </button>
          
          <button
            onClick={clearLogs}
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200"
          >
            <Trash2 className="h-4 w-4" />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Logs Container */}
      <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-96 overflow-y-auto">
        {filteredLogs.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            No logs available. Start the maintenance cycle to see logs.
          </div>
        ) : (
          filteredLogs.map((log, index) => {
            const level = getLogLevel(log);
            const colorClass = getLogColor(level);
            
            return (
              <div
                key={index}
                className={`mb-1 p-2 rounded ${
                  level !== 'default' ? colorClass : ''
                }`}
              >
                <span className="text-gray-400">
                  {new Date().toLocaleTimeString()}
                </span>
                <span className="ml-2">{log}</span>
              </div>
            );
          })
        )}
        <div ref={logsEndRef} />
      </div>

      {/* Log Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
        <div className="bg-gray-50 p-3 rounded-md text-center">
          <div className="text-2xl font-bold text-gray-600">
            {logs.filter(log => log.includes('[INFO]')).length}
          </div>
          <div className="text-gray-500">Info</div>
        </div>
        <div className="bg-green-50 p-3 rounded-md text-center">
          <div className="text-2xl font-bold text-green-600">
            {logs.filter(log => log.includes('[SUCCESS]')).length}
          </div>
          <div className="text-green-500">Success</div>
        </div>
        <div className="bg-yellow-50 p-3 rounded-md text-center">
          <div className="text-2xl font-bold text-yellow-600">
            {logs.filter(log => log.includes('[WARNING]')).length}
          </div>
          <div className="text-yellow-500">Warning</div>
        </div>
        <div className="bg-red-50 p-3 rounded-md text-center">
          <div className="text-2xl font-bold text-red-600">
            {logs.filter(log => log.includes('[ERROR]')).length}
          </div>
          <div className="text-red-500">Error</div>
        </div>
        <div className="bg-blue-50 p-3 rounded-md text-center">
          <div className="text-2xl font-bold text-blue-600">
            {logs.filter(log => log.includes('[DEBUG]')).length}
          </div>
          <div className="text-blue-500">Debug</div>
        </div>
      </div>
    </div>
  );
}
