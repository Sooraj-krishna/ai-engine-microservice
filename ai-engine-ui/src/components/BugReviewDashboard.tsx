'use client';

import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '@/lib/config';
import { Bug as BugIcon, Zap, Shield, AlertTriangle, CheckCircle, RefreshCcw, Trash2, XCircle } from 'lucide-react';
import BugProgressTracker from './BugProgressTracker';

interface Bug {
  id: string;
  type: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  target_file: string;
  detected_at: string;
  framework: string;
  language: string;
}

interface BugsBySeverity {
  critical: Bug[];
  high: Bug[];
  medium: Bug[];
  low: Bug[];
}

interface InProgressBug {
  bug_id: string;
  severity: string;
  status: string;
  bug: {
    type: string;
    description: string;
  };
  processing_started_at: string;
}

const BugReviewDashboard: React.FC = () => {
  const [bugs, setBugs] = useState<BugsBySeverity>({
    critical: [],
    high: [],
    medium: [],
    low: []
  });
  const [summary, setSummary] = useState({ critical: 0, high: 0, medium: 0, low: 0 });
  const [activeTab, setActiveTab] = useState<'critical' | 'high' | 'medium' | 'low' | 'in_progress'>('critical');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState<string | null>(null);
  const [inProgressBugs, setInProgressBugs] = useState<InProgressBug[]>([]);

  useEffect(() => {
    fetchPendingBugs();
    fetchInProgressBugs();
    
    const interval = setInterval(fetchInProgressBugs, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchPendingBugs = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/bugs/pending`);
      const data = await response.json();
      
      setBugs(data.bugs_by_severity);
      setSummary(data.summary);
      setError(null);
    } catch (err) {
      setError('Failed to load bugs. Make sure the server is running.');
      console.error('Error fetching bugs:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchInProgressBugs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/bugs/in-progress`);
      const data = await response.json();
      setInProgressBugs(data.bugs || []);
    } catch (err) {
      console.error('Error fetching in-progress bugs:', err);
    }
  };

  const approveBug = async (bugId: string) => {
    try {
      setApproving(bugId);
      const response = await fetch(`${API_BASE_URL}/bugs/${bugId}/approve`, {
        method: 'POST'
      });
      
      if (response.ok) {
        if (activeTab !== 'in_progress') {
          setBugs(prev => ({
            ...prev,
            [activeTab]: prev[activeTab].filter(bug => bug.id !== bugId)
          }));
          setSummary(prev => ({
            ...prev,
            [activeTab]: prev[activeTab] - 1
          }));
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`Failed to approve bug: ${errorData.error || response.statusText}`);
      }
    } catch (err) {
      alert('Error approving bug: Connection failed');
      console.error(err);
    } finally {
      setApproving(null);
    }
  };

  const approveBySeverity = async (severity: string) => {
    if (!confirm(`Approve all ${summary[severity as keyof typeof summary]} ${severity} severity bugs?`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/bugs/approve-batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ severities: [severity] })
      });
      
      if (response.ok) {
        fetchPendingBugs();
      }
    } catch (err) {
      alert('Error approving bugs');
      console.error(err);
    }
  };

  const clearFailedBugs = async () => {
    if (!confirm('Clear all failed bugs from the queue?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/bugs/failed`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchPendingBugs();
      }
    } catch (err) {
      alert('Error clearing failed bugs');
      console.error(err);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500';
      case 'high': return 'text-orange-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-green-500';
      default: return 'text-zinc-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center space-y-4">
          <RefreshCcw className="h-8 w-8 text-white animate-spin" />
          <p className="text-zinc-500 uppercase tracking-widest text-xs font-bold">Synchronizing Intelligence...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="premium-card p-12 text-center max-w-2xl mx-auto my-20">
        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-6" />
        <h3 className="text-2xl font-bold text-white mb-4 uppercase tracking-tighter">{error}</h3>
        <button 
          onClick={fetchPendingBugs}
          className="shimmer-button mt-4"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const totalBugs = summary.critical + summary.high + summary.medium + summary.low;

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
        <div>
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <BugIcon className="h-5 w-5 text-black" />
            </div>
            <h1 className="text-4xl font-bold text-white uppercase tracking-tighter">Queue Dashboard</h1>
          </div>
          <p className="text-zinc-500 font-light text-lg">
            {totalBugs} security and logic anomalies awaiting autonomous resolution.
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button 
            onClick={fetchPendingBugs} 
            className="glass-button flex items-center space-x-2"
          >
            <RefreshCcw className="h-4 w-4" />
            <span>Sync</span>
          </button>
          <button 
            onClick={clearFailedBugs} 
            className="glass-button flex items-center space-x-2 border-red-500/30 text-red-400 hover:bg-red-500/10"
          >
            <Trash2 className="h-4 w-4" />
            <span>Purge Failed</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-10 p-1 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl">
        {(['critical', 'high', 'medium', 'low'] as const).map(severity => (
          <button
            key={severity}
            onClick={() => setActiveTab(severity)}
            className={`flex-1 flex items-center justify-center space-x-3 px-6 py-4 rounded-xl transition-all duration-300 ${
              activeTab === severity 
                ? 'bg-white text-black shadow-xl' 
                : 'text-zinc-500 hover:text-white hover:bg-white/5'
            }`}
          >
            <span className={`text-xs font-black uppercase tracking-widest ${activeTab === severity ? 'text-black' : getSeverityColor(severity)}`}>
              {severity}
            </span>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${activeTab === severity ? 'bg-black/10' : 'bg-white/5'}`}>
              {summary[severity]}
            </span>
          </button>
        ))}
        <button
          onClick={() => setActiveTab('in_progress')}
          className={`flex-1 flex items-center justify-center space-x-3 px-6 py-4 rounded-xl transition-all duration-300 ${
            activeTab === 'in_progress' 
              ? 'bg-white text-black shadow-xl' 
              : 'text-zinc-500 hover:text-white hover:bg-white/5'
          }`}
        >
          <Zap className={`h-4 w-4 ${activeTab === 'in_progress' ? 'text-black' : 'text-blue-400'}`} />
          <span className="text-xs font-black uppercase tracking-widest">Active Fixes</span>
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${activeTab === 'in_progress' ? 'bg-black/10' : 'bg-white/5'}`}>
            {inProgressBugs.length}
          </span>
        </button>
      </div>

      {/* Content */}
      <div className="min-h-[400px]">
        {activeTab === 'in_progress' ? (
          <div className="space-y-6">
            {inProgressBugs.length === 0 ? (
              <div className="premium-card p-20 text-center">
                <CheckCircle className="h-12 w-12 text-zinc-700 mx-auto mb-6" />
                <p className="text-zinc-500 uppercase tracking-widest text-xs font-bold">No active fix operations in progress</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6">
                {inProgressBugs.map((bug) => (
                  <div key={bug.bug_id} className="premium-card p-1">
                    <BugProgressTracker 
                      bugId={bug.bug_id}
                      refreshInterval={2000}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-8">
            {bugs[activeTab as keyof BugsBySeverity].length === 0 ? (
              <div className="premium-card p-20 text-center">
                <CheckCircle className="h-12 w-12 text-zinc-700 mx-auto mb-6" />
                <p className="text-zinc-500 uppercase tracking-widest text-xs font-bold">No {activeTab} anomalies detected</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {bugs[activeTab as keyof BugsBySeverity].map((bug) => (
                  <div key={bug.id} className="group premium-card p-8 transition-all duration-500 hover:border-white/30 h-full flex flex-col">
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full animate-pulse ${
                          bug.severity === 'critical' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 
                          bug.severity === 'high' ? 'bg-orange-500' : 
                          bug.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                        }`} />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500">
                          {bug.type.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <span className="text-[10px] font-bold text-zinc-600 bg-white/5 px-2.5 py-1 rounded-md uppercase tracking-widest">
                        ID: {bug.id.slice(0, 8)}
                      </span>
                    </div>

                    <h3 className="text-xl font-bold text-white mb-4 leading-tight transition-all">
                      {bug.description}
                    </h3>

                    <div className="grid grid-cols-2 gap-4 mb-8 p-4 bg-white/[0.02] rounded-xl border border-white/5 mt-auto">
                      <div>
                        <p className="text-[9px] uppercase tracking-widest text-zinc-600 font-bold mb-1">Target Resource</p>
                        <p className="text-sm text-zinc-400 font-mono truncate">{bug.target_file || 'system'}</p>
                      </div>
                      <div>
                        <p className="text-[9px] uppercase tracking-widest text-zinc-600 font-bold mb-1">Technology Stack</p>
                        <p className="text-sm text-zinc-400">{bug.framework} / {bug.language}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => approveBug(bug.id)}
                        disabled={approving === bug.id}
                        className="flex-1 px-6 py-4 bg-white text-black text-[10px] font-black uppercase tracking-[0.2em] rounded-full hover:bg-zinc-200 transition-all disabled:opacity-50 flex items-center justify-center space-x-3 shadow-[0_0_20px_-5px_rgba(255,255,255,0.2)]"
                      >
                        {approving === bug.id ? (
                          <>
                            <RefreshCcw className="h-3.5 w-3.5 animate-spin" />
                            <span>Processing...</span>
                          </>
                        ) : (
                          <>
                            <Shield className="h-3.5 w-3.5" />
                            <span>Authorize Fix</span>
                          </>
                        )}
                      </button>
                      <button className="p-4 bg-white/5 border border-white/10 text-zinc-500 hover:text-white hover:bg-white/10 hover:border-white/20 rounded-full transition-all active:scale-95">
                        <XCircle className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {summary[activeTab as keyof typeof summary] > 0 && (
              <div className="flex justify-center pt-8">
                <button 
                  onClick={() => approveBySeverity(activeTab)}
                  className="glass-button px-12 py-4 border-white/20 hover:bg-white hover:text-black transition-all group"
                >
                  <span className="uppercase tracking-[0.3em] text-xs font-black">Authorize Batch Resolution</span>
                  <span className="ml-2 opacity-50 group-hover:opacity-100">({summary[activeTab]})</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BugReviewDashboard;
