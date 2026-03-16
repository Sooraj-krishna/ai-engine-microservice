'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Loader2, CheckCircle2, Clock, PlayCircle, XCircle } from 'lucide-react';

// Types remain the same
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
}

interface ImplementationSummary {
  total_selected: number;
  by_status: {
    pending: number;
    in_progress: number;
    completed: number;
    cancelled: number;
  };
  pending: number;
  in_progress: number;
  completed: number;
  cancelled: number;
  by_priority: {
    high: number;
    medium: number;
    low: number;
  };
  high: number;
  medium: number;
  low: number;
  features: SelectedFeature[];
}

export default function FeatureImplementationStatus() {
  const [summary, setSummary] = useState<ImplementationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedFeature, setExpandedFeature] = useState<string | null>(null);

  // Fetch summary on load
  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchSummary = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/features/implementation-status');
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
    try {
      const response = await fetch(`http://localhost:8000/api/features/${featureId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        fetchSummary(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to update feature status:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="h-5 w-5 text-green-400" />;
      case 'in_progress': return <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />;
      case 'pending': return <Clock className="h-5 w-5 text-zinc-400" />;
      case 'cancelled': return <XCircle className="h-5 w-5 text-red-400" />;
      default: return <Clock className="h-5 w-5 text-zinc-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'in_progress': return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'pending': return 'bg-white/5 text-white/60 border-white/10';
      case 'cancelled': return 'bg-red-500/10 text-red-400 border-red-500/20';
      default: return 'bg-white/5 text-white/60 border-white/10';
    }
  };

  const calculateProgress = () => {
    if (!summary || summary.total_selected === 0) return 0;
    const completed = summary.completed || 0;
    return Math.round((completed / summary.total_selected) * 100);
  };

  if (loading && !summary) {
    return (
      <div className="flex justify-center p-8 bg-white/5 border border-white/10 rounded-2xl">
        <Loader2 className="h-8 w-8 animate-spin text-white/40" />
      </div>
    );
  }

  if (!summary || summary.features.length === 0) {
    return (
      <div className="text-center p-8 bg-white/5 border border-white/10 rounded-2xl">
        <h3 className="text-lg font-medium text-white">No Features Tracked</h3>
        <p className="text-white/50 mt-2">Select features from recommendations to start tracking.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/5 border border-white/10 p-4 rounded-xl">
          <div className="text-2xl font-bold text-white">{summary.total_selected}</div>
          <div className="text-xs uppercase tracking-wider text-white/40 font-bold mt-1">Total Selected</div>
        </div>
        <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl">
          <div className="text-2xl font-bold text-blue-400">{summary.in_progress}</div>
          <div className="text-xs uppercase tracking-wider text-blue-500/60 font-bold mt-1">In Progress</div>
        </div>
        <div className="bg-green-500/10 border border-green-500/20 p-4 rounded-xl">
          <div className="text-2xl font-bold text-green-400">{summary.completed}</div>
          <div className="text-xs uppercase tracking-wider text-green-500/60 font-bold mt-1">Completed</div>
        </div>
        <div className="bg-white/5 border border-white/10 p-4 rounded-xl">
          <div className="text-2xl font-bold text-white/60">{summary.pending}</div>
          <div className="text-xs uppercase tracking-wider text-white/30 font-bold mt-1">Pending</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-white bg-white/10">
              Overall Progress
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs font-bold inline-block text-white">
              {calculateProgress()}%
            </span>
          </div>
        </div>
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-white/10">
          <div 
            style={{ width: `${calculateProgress()}%` }} 
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-white transition-all duration-500"
          ></div>
        </div>
      </div>

      {/* Feature List */}
      <div className="space-y-3">
        {summary.features.map((feature) => (
          <div 
            key={feature.id} 
            className={`border rounded-xl transition-all duration-200 overflow-hidden ${
              expandedFeature === feature.id 
                ? 'bg-white/10 border-white/20' 
                : 'bg-white/5 border-white/10 hover:bg-white/[0.08]'
            }`}
          >
            <div 
              className="p-4 flex items-center justify-between cursor-pointer"
              onClick={() => setExpandedFeature(expandedFeature === feature.id ? null : feature.id)}
            >
              <div className="flex items-center gap-4 flex-1">
                <div className={`p-2 rounded-lg border ${getStatusColor(feature.implementation_status)}`}>
                  {getStatusIcon(feature.implementation_status)}
                </div>
                <div>
                  <h4 className="font-semibold text-white">{feature.feature_name}</h4>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-white/40 uppercase tracking-wider">{feature.category}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full border ${
                      feature.priority_score > 7 ? 'text-red-400 border-red-400/30' : 
                      feature.priority_score > 4 ? 'text-yellow-400 border-yellow-400/30' : 
                      'text-green-400 border-green-400/30'
                    }`}>
                      Priority {feature.priority_score}/10
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${getStatusColor(feature.implementation_status)}`}>
                  {feature.implementation_status.replace('_', ' ')}
                </span>
                {expandedFeature === feature.id ? 
                  <ChevronUp className="h-5 w-5 text-white/40" /> : 
                  <ChevronDown className="h-5 w-5 text-white/40" />
                }
              </div>
            </div>

            {/* Expanded Details */}
            {expandedFeature === feature.id && (
              <div className="px-4 pb-4 pt-0 border-t border-white/10 mt-2 bg-black/20">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                  <div>
                    <h5 className="text-xs font-bold text-white/40 uppercase tracking-widest mb-2">Impact Analysis</h5>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between py-1 border-b border-white/5">
                        <span className="text-white/60">Estimated Effort</span>
                        <span className="text-white font-medium">{feature.estimated_effort}</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-white/5">
                        <span className="text-white/60">Business Impact</span>
                        <span className="text-white font-medium">{feature.business_impact}</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-white/5">
                        <span className="text-white/60">Selected At</span>
                        <span className="text-white font-medium">
                          {new Date(feature.selected_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h5 className="text-xs font-bold text-white/40 uppercase tracking-widest mb-2">Actions</h5>
                    <div className="flex flex-wrap gap-2">
                      {feature.implementation_status !== 'completed' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            updateFeatureStatus(feature.id, 'completed');
                          }}
                          className="flex items-center gap-2 px-3 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 text-xs font-bold uppercase tracking-wider rounded-lg border border-green-500/20 transition-all"
                        >
                          <CheckCircle2 className="h-4 w-4" />
                          Mark Completed
                        </button>
                      )}
                      
                      {feature.implementation_status !== 'in_progress' && feature.implementation_status !== 'completed' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            updateFeatureStatus(feature.id, 'in_progress');
                          }}
                          className="flex items-center gap-2 px-3 py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 text-xs font-bold uppercase tracking-wider rounded-lg border border-blue-500/20 transition-all"
                        >
                          <PlayCircle className="h-4 w-4" />
                          Start Implementing
                        </button>
                      )}

                      {feature.implementation_status !== 'cancelled' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            updateFeatureStatus(feature.id, 'cancelled');
                          }}
                          className="flex items-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 text-white/60 text-xs font-bold uppercase tracking-wider rounded-lg border border-white/10 transition-all"
                        >
                          <XCircle className="h-4 w-4" />
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
