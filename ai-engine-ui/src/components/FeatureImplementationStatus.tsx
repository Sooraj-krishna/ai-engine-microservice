'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Loader2, CheckCircle2, Clock, PlayCircle, XCircle } from 'lucide-react';

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
      const response = await fetch('http://localhost:8000/implementation-summary');
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
      const response = await fetch(`http://localhost:8000/feature-status/${featureId}`, {
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
    <div className="glass-card rounded-xl p-6 smooth-transition">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-r from-purple-500 to-blue-500 p-2 rounded-lg">
            <CheckCircle2 className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gradient">Feature Implementation Status</h2>
            <p className="text-sm text-gray-600">Track your selected features</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {summary.by_status.cancelled > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowCancelled(!showCancelled)}
              className="hover:bg-gray-100 text-xs"
            >
              {showCancelled ? 'Hide' : 'Show'} Cancelled ({summary.by_status.cancelled})
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="hover:bg-purple-100"
          >
            {isExpanded ? (
              <ChevronUp className="h-5 w-5" />
            ) : (
              <ChevronDown className="h-5 w-5" />
            )}
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
          <div className="text-3xl font-bold text-purple-700">{summary.total_selected}</div>
          <div className="text-xs text-purple-600">Total Selected</div>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
          <div className="text-3xl font-bold text-blue-700">{summary.by_status.in_progress}</div>
          <div className="text-xs text-blue-600">In Progress</div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
          <div className="text-3xl font-bold text-green-700">{summary.by_status.completed}</div>
          <div className="text-xs text-green-600">Completed</div>
        </div>
        <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-4 border border-gray-200">
          <div className="text-3xl font-bold text-gray-700">{summary.by_status.pending}</div>
          <div className="text-xs text-gray-600">Pending</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm font-bold text-purple-700">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="h-3 bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Expanded Feature List */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-6 animate-in fade-in duration-300">
          {loading && (
            <div className="flex items-center justify-center py-8 col-span-2">
              <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
            </div>
          )}
          
          {!loading && displayFeatures.map((feature) => (
            <div
              key={feature.id}
              className="bg-white/80 border border-gray-200 rounded-lg p-3 hover:shadow-lg smooth-transition"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {getStatusIcon(feature.implementation_status)}
                    <h3 className="font-semibold text-sm text-gray-900">{feature.feature_name}</h3>
                  </div>
                  <p className="text-xs text-gray-600">{feature.category}</p>
                </div>
                <Badge className={`${getStatusColor(feature.implementation_status)} border capitalize text-xs`}>
                  {feature.implementation_status.replace('_', ' ')}
                </Badge>
              </div>

              <div className="grid grid-cols-3 gap-2 mb-2 text-xs">
                <div>
                  <span className="text-gray-500">Priority:</span>
                  <span className="ml-1 font-medium text-gray-900">{feature.priority_score}/10</span>
                </div>
                <div>
                  <span className="text-gray-500">Effort:</span>
                  <span className="ml-1 font-medium text-gray-900">{feature.estimated_effort}</span>
                </div>
                <div>
                  <span className="text-gray-500">Impact:</span>
                  <span className="ml-1 font-medium text-gray-900 capitalize">{feature.business_impact}</span>
                </div>
              </div>

              <div className="flex gap-2">
                {feature.implementation_status === 'pending' && (
                  <Button
                    size="sm"
                    onClick={() => updateFeatureStatus(feature.id, 'in_progress')}
                    disabled={updatingStatus === feature.id}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-xs py-1 h-7"
                  >
                    {updatingStatus === feature.id ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      'Start'
                    )}
                  </Button>
                )}
                {feature.implementation_status === 'in_progress' && (
                  <>
                    <Button
                      size="sm"
                      onClick={() => updateFeatureStatus(feature.id, 'completed')}
                      disabled={updatingStatus === feature.id}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white text-xs py-1 h-7"
                    >
                      {updatingStatus === feature.id ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        'Complete'
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => updateFeatureStatus(feature.id, 'cancelled')}
                      disabled={updatingStatus === feature.id}
                      className="flex-1 text-xs py-1 h-7"
                    >
                      Cancel
                    </Button>
                  </>
                )}
              </div>

              {feature.status_updated_at && (
                <div className="mt-2 text-xs text-gray-500">
                  Updated: {new Date(feature.status_updated_at).toLocaleString()}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
