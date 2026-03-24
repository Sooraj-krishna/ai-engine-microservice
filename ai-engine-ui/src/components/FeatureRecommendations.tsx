/**
 * Feature Recommendations Component
 * Displays competitive analysis results and allows feature selection
 */

'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface Feature {
  id: string;
  name: string;
  category: string;
  description: string;
  found_in: string[];
  frequency: string;
  frequency_percentage: string;
  complexity: string;
  priority_score: number;
  estimated_effort: string;
  business_impact: string;
  implementation_notes: string;
}

interface FeatureRecommendationsProps {
  onFeatureSelect?: (featureId: string) => void;
  onOpenChatbot?: (featureId: string, sessionId: string) => void;
}

export default function FeatureRecommendations({ onFeatureSelect, onOpenChatbot }: FeatureRecommendationsProps) {
  const [recommendations, setRecommendations] = useState<Feature[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>([]);

  // Fetch recommendations on mount
  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/features/recommendations');
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      // Don't show error to user immediately, just log it
    } finally {
      setLoading(false);
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/task/${taskId}`);
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'completed') {
            clearInterval(pollInterval);
            setAnalyzing(false);
            setAnalysisProgress(100);
            fetchRecommendations(); // Refresh the list
          } else if (data.status === 'failed') {
            clearInterval(pollInterval);
            setAnalyzing(false);
            setError('Analysis failed. Please try again.');
          } else {
            // Update progress if available, otherwise just keep showing loading
            if (data.progress) setAnalysisProgress(data.progress);
          }
        }
      } catch (err) {
        console.error('Task polling failed:', err);
      }
    }, 2000);
  };

  const triggerAnalysis = async (isProfessional: boolean = false) => {
    try {
      setAnalyzing(true);
      setAnalysisProgress(0);
      setError(null);
      
      const endpoint = isProfessional 
        ? 'http://localhost:8000/api/features/analyze-professional' 
        : 'http://localhost:8000/api/features/analyze';
        
      const response = await fetch(endpoint, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        if (data.task_id) {
          pollTaskStatus(data.task_id);
        } else {
          // Direct response
          setAnalyzing(false);
          setAnalysisProgress(100);
          fetchRecommendations();
        }
      } else {
        throw new Error('Analysis request failed');
      }
    } catch (err) {
      setAnalyzing(false);
      setError('Failed to start analysis. Please check backend connection.');
      console.error(err);
    }
  };

  const handleSelectFeature = async (featureId: string) => {
    try {
      // Add to local selection
      if (!selectedFeatures.includes(featureId)) {
        setSelectedFeatures([...selectedFeatures, featureId]);
      }
      
      // Call backend to save selection
      await fetch('http://localhost:8000/api/features/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature_ids: [featureId] })
      });
      
      // Notify parent
      if (onFeatureSelect) onFeatureSelect(featureId);
      
    } catch (err) {
      console.error('Failed to select feature:', err);
    }
  };

  const getPriorityColor = (score: number) => {
    if (score >= 8) return 'text-red-400 border-red-400/30';
    if (score >= 5) return 'text-yellow-400 border-yellow-400/30';
    return 'text-green-400 border-green-400/30';
  };

  const getPriorityLabel = (score: number) => {
    if (score >= 8) return 'High Priority';
    if (score >= 5) return 'Medium Priority';
    return 'Low Priority';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
        <div>
          <h2 className="text-3xl font-bold uppercase tracking-wider text-white">Feature Recommendations</h2>
          <p className="text-white/50 mt-2">Analyze competitor websites to discover missing features</p>
        </div>
        
        <div className="flex gap-3">
          <button 
            onClick={() => triggerAnalysis(false)}
            disabled={analyzing}
            className="px-6 py-3 bg-white text-black hover:bg-gray-100 rounded-full font-bold uppercase tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm shadow-lg"
          >
            {analyzing ? 'Analyzing...' : 'Run Standard Analysis'}
          </button>
          <button 
            onClick={() => triggerAnalysis(true)}
            disabled={analyzing}
            className="px-6 py-3 bg-white/5 hover:bg-white/10 text-white border border-white/20 rounded-full font-bold uppercase tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            Run Professional Analysis
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl flex items-center gap-2">
          <span>⚠️</span>
          {error}
        </div>
      )}

      {analyzing && (
        <div className="space-y-2 bg-white/5 border border-white/10 p-8 rounded-2xl text-center">
          <div className="animate-spin h-8 w-8 border-4 border-white/20 border-t-white rounded-full mx-auto mb-4"></div>
          <h3 className="text-xl font-bold text-white uppercase tracking-wider">Analyzing Market...</h3>
          <p className="text-white/40">Scanning competitor features and gaps</p>
          <div className="w-full max-w-md mx-auto bg-white/10 rounded-full h-2 mt-4 overflow-hidden">
            <div 
              className="bg-white h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.max(5, analysisProgress)}%` }}
            ></div>
          </div>
        </div>
      )}

      {!analyzing && recommendations.length === 0 && !loading && (
        <div className="text-center py-16 bg-white/5 border border-white/10 rounded-2xl">
          <h3 className="text-xl font-bold text-white">No Recommendations Yet</h3>
          <p className="text-white/50 mt-2 mb-6">Run an analysis to see what features you're missing.</p>
          <button 
            onClick={() => triggerAnalysis(true)}
            className="px-8 py-3 bg-white text-black hover:bg-gray-100 rounded-full font-bold uppercase tracking-wider transition-all"
          >
            Start First Analysis
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {recommendations.map((feature) => (
          <div 
            key={feature.id}
            className="bg-white/5 border border-white/10 hover:border-white/20 hover:bg-white/[0.08] transition-all rounded-2xl overflow-hidden"
          >
            <div 
              className="p-6 cursor-pointer"
              onClick={() => setExpandedId(expandedId === feature.id ? null : feature.id)}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl border ${getPriorityColor(feature.priority_score)} bg-opacity-10`}>
                    <span className="text-xl font-bold block text-center min-w-[1.5rem]">{feature.priority_score}</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">{feature.name}</h3>
                    <div className="flex flex-wrap items-center gap-2 mt-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-white/40 bg-white/5 px-2 py-1 rounded-md">{feature.category}</span>
                      <span className={`text-xs font-bold uppercase tracking-wider px-2 py-1 rounded-md border ${getPriorityColor(feature.priority_score)}`}>
                        {getPriorityLabel(feature.priority_score)}
                      </span>
                      <span className="text-xs font-bold uppercase tracking-wider text-white/40 px-2 py-1">
                        Impact: <span className="text-white">{feature.business_impact}</span>
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                   {selectedFeatures.includes(feature.id) ? (
                     <span className="px-4 py-2 bg-green-500/20 text-green-400 border border-green-500/30 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-2">
                       <span>✓</span> Selected
                     </span>
                   ) : (
                     <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectFeature(feature.id);
                        }}
                        className="px-6 py-2 bg-white text-black hover:bg-gray-100 rounded-full text-xs font-bold uppercase tracking-wider transition-all shadow-md"
                      >
                        Select Feature
                      </button>
                   )}
                   {expandedId === feature.id ? <ChevronUp className="text-white/40" /> : <ChevronDown className="text-white/40" />}
                </div>
              </div>
            </div>

            {expandedId === feature.id && (
              <div className="border-t border-white/10 bg-black/20 p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-widest text-white/40 mb-3">Description</h4>
                    <p className="text-white/80 leading-relaxed mb-6">{feature.description}</p>
                    
                    <h4 className="text-xs font-bold uppercase tracking-widest text-white/40 mb-3">Found In Competitors</h4>
                    <div className="flex flex-wrap gap-2 mb-6">
                      {feature.found_in.map((comp, idx) => (
                        <span key={idx} className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-white/70">
                          {comp}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-widest text-white/40 mb-3">Implementation Notes</h4>
                    <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-sm text-white/70 leading-relaxed font-mono">
                      {feature.implementation_notes}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 mt-6">
                      <div>
                        <span className="block text-xs text-white/40 uppercase tracking-wider mb-1">Complexity</span>
                        <span className="block text-white font-medium">{feature.complexity}</span>
                      </div>
                      <div>
                        <span className="block text-xs text-white/40 uppercase tracking-wider mb-1">Estimated Effort</span>
                        <span className="block text-white font-medium">{feature.estimated_effort}</span>
                      </div>
                    </div>

                    <div className="mt-6 pt-6 border-t border-white/5">
                        <button 
                           onClick={() => onOpenChatbot && onOpenChatbot(feature.id, 'new')}
                           className="w-full py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-lg text-sm font-bold uppercase tracking-wider transition-all"
                        >
                           Ask AI Assistant about this feature
                        </button>
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
