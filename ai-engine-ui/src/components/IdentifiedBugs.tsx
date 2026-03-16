'use client';

import React, { useEffect, useState } from 'react';
import {
  Bug,
  FileCode,
  AlertTriangle,
  ServerCrash,
  FileText,
  CheckCircle,
  WifiOff,
  LayoutGrid,
  Cpu,
  Database,
  Zap,
  XCircle,
  Terminal,
  Wifi,
} from 'lucide-react';

interface BugInfo {
  type: string;
  description: string;
  details: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  timestamp: string;
}

interface IdentifiedBugsProps {
  issues?: {
    type: string;
    data: BugInfo;
    description: string;
    details: string;
  }[];
}

const getBugIcon = (type: string) => {
  switch (type) {
    case 'Deployment Configuration Error':
      return <ServerCrash className="h-6 w-6 text-cyan-400" />;
    case 'Broken or Missing Static Assets':
      return <FileText className="h-6 w-6 text-yellow-500" />;
    case 'Data Persistence and State Management Error':
      return <AlertTriangle className="h-6 w-6 text-blue-500" />;
    case 'Network Connectivity Failure':
      return <WifiOff className="h-6 w-6 text-orange-500" />;
    case 'UI Rendering Error':
      return <LayoutGrid className="h-6 w-6 text-pink-500" />;
    case 'Runtime Exception':
      return <XCircle className="h-6 w-6 text-red-600" />;
    case 'Console Error':
      return <Terminal className="h-6 w-6 text-gray-600" />;
    case 'Console Warning':
      return <Terminal className="h-6 w-6 text-yellow-600" />;
    case 'Logic Error':
      return <Zap className="h-6 w-6 text-purple-500" />;
    case 'Backend Response Error':
      return <Database className="h-6 w-6 text-indigo-600" />;
    case 'Performance Bottleneck':
      return <Cpu className="h-6 w-6 text-teal-500" />;
    default:
      return <Bug className="h-6 w-6 text-gray-500" />;
  }
};

const extractFilePath = (details: string): string | null => {
  const match = details.match(/in: (.*)/);
  if (match && match[1]) return match[1];
  const urlMatch = details.match(/URL: (.*)/);
  if (urlMatch && urlMatch[1]) return urlMatch[1];
  return details;
};

export function IdentifiedBugs({ issues = [] }: IdentifiedBugsProps) {
  const [liveBugs, setLiveBugs] = useState<BugInfo[]>([]);

  useEffect(() => {
    // Capture Console Errors
    const originalConsoleError = console.error;
    console.error = (...args) => {
      addBug('Console Error', args.join(' '), 'High');
      originalConsoleError(...args);
    };

    // Capture Console Warnings
    const originalConsoleWarn = console.warn;
    console.warn = (...args) => {
      addBug('Console Warning', args.join(' '), 'Medium');
      originalConsoleWarn(...args);
    };

    // Capture Uncaught Runtime Errors
    window.onerror = (msg, src, line, col, err) => {
      addBug(
        'Runtime Exception',
        `${msg} at ${src}:${line}:${col}`,
        'Critical'
      );
      return false;
    };

    // Capture Unhandled Promise Rejections
    window.onunhandledrejection = (event: PromiseRejectionEvent) => {
      addBug('Unhandled Promise Rejection', String(event.reason), 'High');
    };

    // Capture Network Failures (fetch)
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      try {
        const response = await originalFetch(...args);
        if (!response.ok) {
          addBug(
            'Network Connectivity Failure',
            `Fetch failed: ${args[0]} → ${response.status} ${response.statusText}`,
            'High'
          );
        }
        return response;
      } catch (error: any) {
        addBug(
          'Network Connectivity Failure',
          `Fetch Error: ${args[0]} → ${error.message}`,
          'Critical'
        );
        throw error;
      }
    };

    // Restore on unmount
    return () => {
      console.error = originalConsoleError;
      console.warn = originalConsoleWarn;
      window.onerror = null;
      window.onunhandledrejection = null;
      window.fetch = originalFetch;
    };
  }, []);

  const addBug = (type: string, details: string, severity: BugInfo['severity']) => {
    const newBug: BugInfo = {
      type,
      description: `${type} detected.`,
      details,
      severity,
      timestamp: new Date().toISOString(),
    };
    setLiveBugs(prev => [newBug, ...prev]);
  };

  const allIssues = [
    ...issues.map(i => i.data),
    ...liveBugs,
  ];

  if (allIssues.length === 0) {
    return (
      <div className="dark-card rounded-lg p-6">
        <h2 className="text-2xl font-bold text-red-gradient mb-4 uppercase tracking-wider">
          Identified Bugs
        </h2>
        <div className="text-center py-8 text-zinc-500">
          <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
          <p className="font-bold uppercase tracking-wider">No bugs detected in the latest scan.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dark-card rounded-lg p-6">
      <h2 className="text-2xl font-bold text-red-gradient mb-4 uppercase tracking-wider">
        Identified Bugs (Real-Time)
      </h2>
      <div className="space-y-4">
        {allIssues.map((bug, index) => (
          <div
            key={index}
            className="bg-zinc-900/50 border border-cyan-900/30 rounded-lg p-4 hover:border-cyan-800/50 transition-all smooth-transition"
          >
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 mt-1">{getBugIcon(bug.type)}</div>
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <p className="font-bold text-lg text-white uppercase tracking-wide">{bug.type}</p>
                  <span
                    className={`px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-lg border ${
                      bug.severity === 'Critical'
                        ? 'bg-cyan-950/50 text-cyan-400 border-cyan-800/50'
                        : bug.severity === 'High'
                        ? 'bg-orange-950/50 text-orange-400 border-orange-800/50'
                        : bug.severity === 'Medium'
                        ? 'bg-yellow-950/50 text-yellow-400 border-yellow-800/50'
                        : 'bg-green-950/50 text-green-400 border-green-800/50'
                    }`}
                  >
                    {bug.severity}
                  </span>
                </div>

                <p className="text-md text-zinc-300 mt-1">{bug.description}</p>

                <div className="mt-3 bg-black/50 border border-zinc-800 rounded-lg p-3 text-sm font-mono">
                  <div className="flex items-center space-x-2">
                    <FileCode className="h-4 w-4 text-cyan-400" />
                    <span className="font-bold text-zinc-400 uppercase tracking-wider">Details:</span>
                    <code className="text-cyan-400 break-all">
                      {extractFilePath(bug.details)}
                    </code>
                  </div>

                  <div className="flex items-center space-x-2 mt-2">
                    <span className="font-bold ml-6 text-zinc-400 uppercase tracking-wider">Detected:</span>
                    <span className="text-zinc-500">
                      {new Date(bug.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}