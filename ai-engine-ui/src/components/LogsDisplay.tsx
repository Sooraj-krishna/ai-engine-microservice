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
      case 'error': return 'text-cyan-400';
      case 'warning': return 'text-yellow-400';
      case 'success': return 'text-green-400';
      case 'debug': return 'text-blue-400';
      case 'info': return 'text-zinc-300';
      default: return 'text-green-400';
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
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Terminal className="h-5 w-5 text-cyan-400" />
            <span className="text-sm font-bold text-white uppercase tracking-wider">
              Terminal ({filteredLogs.length})
            </span>
          </div>
          
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-1 bg-zinc-900 border border-zinc-700 text-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-600"
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
            className={`px-3 py-1 text-xs uppercase tracking-wider font-bold rounded-lg border ${
              isAutoScroll 
                ? 'bg-cyan-900/50 text-cyan-400 border-cyan-800' 
                : 'bg-zinc-900 text-zinc-400 border-zinc-700'
            }`}
          >
            Auto-scroll {isAutoScroll ? 'ON' : 'OFF'}
          </button>
          
          <button
            onClick={downloadLogs}
            className="flex items-center gap-2 px-3 py-1 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-white rounded-lg transition-all text-xs font-bold uppercase tracking-wider"
          >
            <Download className="h-3 w-3" />
            Download
          </button>
          
          <button
            onClick={clearLogs}
            className="flex items-center space-x-1 px-3 py-1 text-xs bg-cyan-900/50 text-cyan-400 border border-cyan-800 rounded-lg hover:bg-cyan-800/50 uppercase tracking-wider font-bold"
          >
            <Trash2 className="h-3 w-3" />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Logs Container */}
      <div className="terminal-display p-4 rounded-lg h-96 overflow-y-auto">
        {filteredLogs.length === 0 ? (
          <div className="text-zinc-600 text-center py-8 font-mono">
            {'>'}_ No logs available. Start the maintenance cycle to see logs.
          </div>
        ) : (
          filteredLogs.map((log, index) => {
            const level = getLogLevel(log);
            const colorClass = getLogColor(level);
            
            return (
              <div
                key={index}
                className={`mb-1 py-1 ${
                  level !== 'default' ? colorClass : 'text-green-400'
                }`}
              >
                <span className="text-zinc-600">
                  {new Date().toLocaleTimeString()}
                </span>
<span className="ml-2"><span className="text-cyan-400">{'>'}</span> {log}</span>
              </div>
            );
          })
        )}
        <div ref={logsEndRef} />
      </div>

      {/* Log Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm mt-4">
        <div className="bg-zinc-900/50 border border-zinc-800 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-zinc-400">
            {logs.filter(log => log.includes('[INFO]')).length}
          </div>
          <div className="text-zinc-500 uppercase tracking-wider text-xs font-bold">Info</div>
        </div>
        <div className="bg-green-950/50 border border-green-800/50 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-green-400">
            {logs.filter(log => log.includes('[SUCCESS]')).length}
          </div>
          <div className="text-green-500 uppercase tracking-wider text-xs font-bold">Success</div>
        </div>
        <div className="bg-yellow-950/50 border border-yellow-800/50 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-yellow-400">
            {logs.filter(log => log.includes('[WARNING]')).length}
          </div>
          <div className="text-yellow-500 uppercase tracking-wider text-xs font-bold">Warning</div>
        </div>
        <div className="bg-cyan-950/50 border border-cyan-800/50 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-cyan-400">
            {logs.filter(log => log.includes('[ERROR]')).length}
          </div>
          <div className="text-cyan-400 uppercase tracking-wider text-xs font-bold">Error</div>
        </div>
        <div className="bg-blue-950/50 border border-blue-800/50 p-3 rounded-lg text-center">
          <div className="text-2xl font-bold text-blue-400">
            {logs.filter(log => log.includes('[DEBUG]')).length}
          </div>
          <div className="text-blue-500 uppercase tracking-wider text-xs font-bold">Debug</div>
        </div>
      </div>
    </div>
  );
}
