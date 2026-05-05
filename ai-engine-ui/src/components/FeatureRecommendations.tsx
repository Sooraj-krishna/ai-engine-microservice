'use client';

import { API_BASE_URL } from '@/lib/config';
import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Sparkles, AlertTriangle, Play, RefreshCw, BarChart, CheckCircle2 } from 'lucide-react';

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
  const [features, setFeatures] = useState<Feature[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzingPremium, setAnalyzingPremium] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(true);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/feature-recommendations`);
      
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        setError('Server returned non-JSON response. API might be unavailable.');
        setLoading(false);
        return;
      }
      
      if (response.ok) {
        const data = await response.json();
        setFeatures(data.feature_gaps || []);
        setSummary(data.summary || null);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to fetch recommendations');
      }
    } catch (error) {
      console.error('Failed to fetch feature recommendations:', error);
      setError('Network error or API unavailable. Run competitive analysis first.');
    } finally {
      setLoading(false);
    }
  };

  const pollTaskStatus = async (taskId: string): Promise<any> => {
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`);
          const data = await response.json();
          
          if (data.ready) {
            clearInterval(interval);
            const resultResponse = await fetch(`${API_BASE_URL}/tasks/${taskId}/result`);
            const resultData = await resultResponse.json();
            resolve(resultData);
          }
        } catch (err) {
          clearInterval(interval);
          reject(err);
        }
      }, 2000);
    });
  };

  const triggerAnalysis = async (isProfessional: boolean = false) => {
    if (isProfessional) setAnalyzingPremium(true);
    else setAnalyzing(true);
    
    setError(null);
    try {
      const urlParam = isProfessional ? 'professional=true' : 'premium=false';
      const response = await fetch(`${API_BASE_URL}/analyze-competitors?${urlParam}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const initialData = await response.json();
        const taskId = initialData.task_id;
        
        await pollTaskStatus(taskId);
        await fetchRecommendations();
        
        setTimeout(() => {
          alert(isProfessional ? '✨ Professional analysis completed!' : '✅ Analysis completed!');
        }, 100);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to trigger analysis');
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setError('Network error triggering analysis');
    } finally {
      setAnalyzing(false);
      setAnalyzingPremium(false);
    }
  };

  const handleSelectFeature = async (featureId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/select-feature`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature_id: featureId })
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedFeature(featureId);
        
        if (onFeatureSelect) onFeatureSelect(featureId);
        
        if (data.success && data.session_id && onOpenChatbot) {
          onOpenChatbot(featureId, data.session_id);
        } else {
          alert(`✅ Feature '${data.feature_name}' queued for implementation.`);
        }
      }
    } catch (error) {
      console.error('Failed to select feature:', error);
    }
  };

  if (loading) {
    return (
      <div className="premium-card p-12 flex flex-col items-center justify-center">
        <RefreshCw className="h-8 w-8 text-zinc-500 animate-spin mb-4" />
        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-500">Loading Intelligence...</p>
      </div>
    );
  }

  // Pre-analysis or zero features state
  if (!features || features.length === 0) {
    if (summary && summary.total_competitors > 0) {
      return (
        <div className="premium-card p-8 border-emerald-500/20 bg-emerald-500/5">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle2 className="h-6 w-6 text-emerald-400" />
            <h3 className="text-sm font-black uppercase tracking-widest text-emerald-400">Competitive Advantage Maintained</h3>
          </div>
          <p className="text-sm text-zinc-300">
            Analyzed {summary.total_competitors} competitor sites. Your platform currently matches or exceeds market feature baselines.
          </p>
        </div>
      );
    }
    
    return (
      <div className="premium-card p-8">
        <div className="mb-8">
          <h3 className="text-xl font-bold text-white tracking-wide mb-2">Market Intelligence</h3>
          <p className="text-sm text-zinc-400">Scan competitors to detect architectural gaps and missing features.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => triggerAnalysis(false)}
            disabled={analyzing || analyzingPremium}
            className="group relative overflow-hidden bg-white/[0.03] hover:bg-white/[0.06] border border-white/10 rounded-xl p-6 text-left transition-all disabled:opacity-50"
          >
            <div className="flex items-center gap-3 mb-3">
              <BarChart className="h-5 w-5 text-zinc-400 group-hover:text-white transition-colors" />
              <span className="text-sm font-black uppercase tracking-widest text-zinc-300 group-hover:text-white transition-colors">
                {analyzing ? 'Scanning...' : 'Standard Scan'}
              </span>
            </div>
            <p className="text-[11px] text-zinc-500 font-medium">Basic UI elements, SEO markers, Accessibility metrics, and Technology Stack discovery.</p>
          </button>
          
          <button
            onClick={() => triggerAnalysis(true)}
            disabled={analyzing || analyzingPremium}
            className="group relative overflow-hidden bg-white/[0.05] hover:bg-white/[0.1] border border-white/20 rounded-xl p-6 text-left transition-all disabled:opacity-50"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 blur-2xl rounded-full -mr-16 -mt-16 pointer-events-none" />
            <div className="flex items-center gap-3 mb-3 relative z-10">
              <Sparkles className="h-5 w-5 text-zinc-300 group-hover:text-white transition-colors" />
              <span className="text-sm font-black uppercase tracking-widest text-white">
                {analyzingPremium ? 'Analyzing...' : 'Deep Scan'}
              </span>
            </div>
            <p className="text-[11px] text-zinc-400 font-medium relative z-10">Comprehensive analysis of business logic, checkout flows, user retention, and advanced architectures.</p>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Summary */}
      <div className="premium-card p-6 flex items-center justify-between cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
        <div>
          <h3 className="text-sm font-black uppercase tracking-[0.2em] text-white mb-1">Feature Delta Analysis</h3>
          <p className="text-[11px] text-zinc-500 font-medium">Scanned {summary?.total_competitors || 0} competitor properties</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex gap-2">
            <span className="px-2 py-1 bg-red-500/10 border border-red-500/20 text-red-400 text-[9px] font-black uppercase tracking-wider rounded">High: {summary?.high_priority || 0}</span>
            <span className="px-2 py-1 bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[9px] font-black uppercase tracking-wider rounded">Med: {summary?.medium_priority || 0}</span>
          </div>
          <button className="p-1 hover:bg-white/5 rounded transition-colors text-zinc-500">
            {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {features.map((feature) => {
            const isHigh = feature.priority_score >= 7;
            const isMed = feature.priority_score >= 4 && feature.priority_score < 7;
            const priorityColor = isHigh ? 'text-red-400' : isMed ? 'text-amber-400' : 'text-blue-400';
            const priorityBg = isHigh ? 'bg-red-500/10 border-red-500/20' : isMed ? 'bg-amber-500/10 border-amber-500/20' : 'bg-blue-500/10 border-blue-500/20';
            const isSelected = selectedFeature === feature.id;

            return (
              <div 
                key={feature.id} 
                className={`premium-card p-6 flex flex-col justify-between transition-all duration-300 ${
                  isSelected ? 'border-white/40 bg-white/[0.05]' : 'hover:bg-white/[0.03] hover:border-white/10'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between mb-4">
                    <div className="pr-4">
                      <h4 className="text-lg font-bold text-white mb-2 leading-tight">{feature.name}</h4>
                      <p className="text-[12px] text-zinc-400 leading-relaxed">{feature.description}</p>
                    </div>
                    <div className={`flex flex-col items-center justify-center p-3 rounded-lg border ${priorityBg} shrink-0`}>
                      <span className={`text-xl font-bold ${priorityColor}`}>{feature.priority_score}</span>
                      <span className={`text-[8px] font-black uppercase tracking-widest ${priorityColor} mt-1`}>Priority</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-5">
                    <div className="bg-black/40 border border-white/5 p-3 rounded-lg">
                      <p className="text-[9px] font-black uppercase tracking-widest text-zinc-600 mb-1">Adoption Rate</p>
                      <p className="text-[11px] text-zinc-300 font-medium">{feature.frequency_percentage}</p>
                    </div>
                    <div className="bg-black/40 border border-white/5 p-3 rounded-lg">
                      <p className="text-[9px] font-black uppercase tracking-widest text-zinc-600 mb-1">Complexity</p>
                      <p className="text-[11px] text-zinc-300 font-medium capitalize">{feature.complexity}</p>
                    </div>
                    <div className="bg-black/40 border border-white/5 p-3 rounded-lg col-span-2">
                      <p className="text-[9px] font-black uppercase tracking-widest text-zinc-600 mb-1">Implementation Notes</p>
                      <p className="text-[11px] text-zinc-400 line-clamp-2">{feature.implementation_notes}</p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleSelectFeature(feature.id)}
                  disabled={isSelected}
                  className={`w-full py-3 rounded-lg flex items-center justify-center gap-2 transition-all ${
                    isSelected 
                      ? 'bg-white text-black font-bold opacity-100 cursor-default' 
                      : 'bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.1] text-white font-medium hover:border-white/[0.2]'
                  }`}
                >
                  {isSelected ? (
                    <>
                      <CheckCircle2 className="h-4 w-4" />
                      <span className="text-xs uppercase tracking-wider">Queued for AI</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4" />
                      <span className="text-xs uppercase tracking-wider">Implement Feature</span>
                    </>
                  )}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
