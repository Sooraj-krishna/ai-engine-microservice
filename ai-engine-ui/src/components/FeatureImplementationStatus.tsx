'use client';

import { API_BASE_URL, WS_BASE_URL } from '@/lib/config';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, ChevronRight, Loader2, CheckCircle2, Clock, PlayCircle, XCircle } from 'lucide-react';

interface SelectedFeature {
  id: string;
  feature_name: string;
  category: string;
  priority_score: number;
  estimated_effort: string;
  business_impact: string;
  selected_at: string;
  implementation_status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  status_updated_at?: string;
  status_history?: {
    status: string;
    notes: string;
    timestamp: string;
  }[];
}

interface ImplementationSummary {
  total_selected: number;
  by_status: {
    pending: number;
    in_progress: number;
    completed: number;
    cancelled: number;
  };
  by_priority: {
    high: number;
    medium: number;
    low: number;
  };
  features: SelectedFeature[];
}

export default function FeatureImplementationStatus() {
  const [isExpanded, setIsExpanded] = useState(true);
  const [summary, setSummary] = useState<ImplementationSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null);
  const [showCancelled, setShowCancelled] = useState(false);

  useEffect(() => {
    fetchSummary();
    // Refresh every 30 seconds
    const interval = setInterval(fetchSummary, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/implementation-summary`);
      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (error) {
      console.error('Failed to fetch implementation summary:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateFeatureStatus = async (featureId: string, newStatus: string) => {
    setUpdatingStatus(featureId);
    try {
      const response = await fetch(`${API_BASE_URL}/feature-status/${featureId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus, notes: `Updated via UI` })
      });

      if (response.ok) {
        await fetchSummary(); // Refresh summary
      }
    } catch (error) {
      console.error('Failed to update feature status:', error);
    } finally {
      setUpdatingStatus(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case 'in_progress':
        return <PlayCircle className="h-4 w-4 text-blue-600" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const calculateProgress = () => {
    if (!summary) return 0;
    const total = summary.total_selected;
    if (total === 0) return 0;
    return Math.round((summary.by_status.completed / total) * 100);
  };

  if (!summary || summary.total_selected === 0) {
    return null; // Don't show if no features selected
  }

  const progress = calculateProgress();
  
  // Filter features based on showCancelled toggle
  const displayFeatures = showCancelled 
    ? summary.features 
    : summary.features.filter(f => f.implementation_status !== 'cancelled');

  return (
    <div className="premium-card p-8 transition-all duration-500">
      <div className="flex items-center justify-between mb-10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-[0_0_20px_-5px_rgba(255,255,255,0.3)]">
            <CheckCircle2 className="h-6 w-6 text-black" />
          </div>
          <div>
            <h2 className="text-xs font-black uppercase tracking-[0.4em] text-white mb-1">Objective Status</h2>
            <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Heuristic Implementation Tracking</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {summary.by_status.cancelled > 0 && (
            <button
              onClick={() => setShowCancelled(!showCancelled)}
              className="text-[10px] font-black uppercase tracking-widest text-zinc-600 hover:text-white transition-colors"
            >
              {showCancelled ? 'Hide' : 'Show'} Cancelled ({summary.by_status.cancelled})
            </button>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 hover:bg-white/5 rounded-full transition-all border border-white/10"
          >
            {isExpanded ? (
              <ChevronUp className="h-4 w-4 text-zinc-400" />
            ) : (
              <ChevronDown className="h-4 w-4 text-zinc-400" />
            )}
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {[
          { label: 'Total Selected', value: summary.total_selected, color: 'text-white' },
          { label: 'In Progress', value: summary.by_status.in_progress, color: 'text-sky-400' },
          { label: 'Completed', value: summary.by_status.completed, color: 'text-emerald-400' },
          { label: 'Pending', value: summary.by_status.pending, color: 'text-zinc-500' },
        ].map((stat, i) => (
          <div key={i} className="bg-white/[0.02] border border-white/5 rounded-2xl p-5 hover:bg-white/[0.04] transition-colors">
            <div className={`text-3xl font-bold tracking-tighter mb-1 ${stat.color}`}>{stat.value}</div>
            <div className="text-[9px] font-black uppercase tracking-[0.2em] text-zinc-600">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Progress Bar */}
      <div className="mb-10">
        <div className="flex justify-between items-end mb-3">
          <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">Overall Implementation Progress</span>
          <span className="text-xl font-bold text-white tabular-nums">{progress}%</span>
        </div>
        <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
          <div
            className="h-full bg-white rounded-full transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(255,255,255,0.5)]"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Expanded Feature List */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
          {loading && (
            <div className="flex items-center justify-center py-12 col-span-2">
              <Loader2 className="h-6 w-6 animate-spin text-zinc-700" />
            </div>
          )}
          
          {!loading && displayFeatures.map((feature) => (
            <div
              key={feature.id}
              className="group bg-white/[0.02] border border-white/5 rounded-2xl p-6 hover:bg-white/[0.04] hover:border-white/10 transition-all duration-300"
            >
              <div className="flex items-start justify-between mb-5">
                <div className="flex-1 pr-4">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="opacity-50 group-hover:opacity-100 transition-opacity">
                      {getStatusIcon(feature.implementation_status)}
                    </div>
                    <h3 className="font-bold text-sm text-white uppercase tracking-tight">{feature.feature_name}</h3>
                  </div>
                  <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest">{feature.category}</p>
                </div>
                <span className={`px-2.5 py-1 text-[8px] font-black uppercase tracking-widest rounded-md border ${
                  feature.implementation_status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                  feature.implementation_status === 'in_progress' ? 'bg-sky-500/10 text-sky-400 border-sky-500/20' :
                  'bg-white/5 text-zinc-500 border-white/10'
                }`}>
                  {feature.implementation_status.replace('_', ' ')}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-black/20 rounded-xl border border-white/5">
                <div>
                  <p className="text-[8px] uppercase tracking-widest text-zinc-600 font-black mb-1">Priority</p>
                  <p className="text-xs text-white font-bold">{feature.priority_score}/10</p>
                </div>
                <div>
                  <p className="text-[8px] uppercase tracking-widest text-zinc-600 font-black mb-1">Effort</p>
                  <p className="text-xs text-white font-bold">{feature.estimated_effort}</p>
                </div>
                <div>
                  <p className="text-[8px] uppercase tracking-widest text-zinc-600 font-black mb-1">Impact</p>
                  <p className="text-xs text-white font-bold capitalize">{feature.business_impact}</p>
                </div>
              </div>
              {/* Progress Detail / Status Notes */}
              {feature.status_history && feature.status_history.length > 0 && (
                <div className="mb-6 animate-in fade-in duration-500">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-white/20 animate-pulse" />
                    <p className="text-[9px] font-black uppercase tracking-widest text-zinc-400">Current Phase</p>
                  </div>
                  <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                    <p className="text-[11px] text-zinc-300 leading-relaxed italic">
                      "{feature.status_history[feature.status_history.length - 1].notes}"
                    </p>
                    
                    {/* Extract PR URL if present */}
                    {feature.status_history[feature.status_history.length - 1].notes.includes('http') && (
                      <div className="mt-4">
                        {(() => {
                          const match = feature.status_history[feature.status_history.length - 1].notes.match(/https?:\/\/[^\s]+/);
                          if (match) {
                            return (
                              <a 
                                href={match[0]} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-500 text-black rounded-lg text-[9px] font-black uppercase tracking-widest hover:bg-emerald-400 transition-all"
                              >
                                Review Pull Request <ChevronRight className="h-3 w-3" />
                              </a>
                            );
                          }
                          return null;
                        })()}
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="flex gap-2">
                {feature.implementation_status === 'pending' && (
                  <button
                    onClick={() => updateFeatureStatus(feature.id, 'in_progress')}
                    disabled={updatingStatus === feature.id}
                    className="flex-1 py-2.5 bg-white text-black text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-zinc-200 transition-all disabled:opacity-50"
                  >
                    {updatingStatus === feature.id ? <Loader2 className="h-3 w-3 animate-spin mx-auto" /> : 'Initialize'}
                  </button>
                )}
                {feature.implementation_status === 'in_progress' && (
                  <>
                    <button
                      onClick={() => updateFeatureStatus(feature.id, 'completed')}
                      disabled={updatingStatus === feature.id}
                      className="flex-1 py-2.5 bg-white text-black text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-zinc-200 transition-all disabled:opacity-50"
                    >
                      {updatingStatus === feature.id ? <Loader2 className="h-3 w-3 animate-spin mx-auto" /> : 'Finalize'}
                    </button>
                    <button
                      onClick={() => updateFeatureStatus(feature.id, 'cancelled')}
                      disabled={updatingStatus === feature.id}
                      className="flex-1 py-2.5 bg-white/5 border border-white/10 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-white/10 transition-all disabled:opacity-50"
                    >
                      Abort
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
