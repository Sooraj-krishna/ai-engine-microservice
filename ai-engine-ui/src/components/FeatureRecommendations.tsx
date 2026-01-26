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
  const [features, setFeatures] = useState<Feature[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzingPremium, setAnalyzingPremium] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPremium, setIsPremium] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/feature-recommendations');
      
      // Check if response is actually JSON before parsing
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

  const triggerAnalysis = async (isProfessional: boolean = false) => {
    if (isProfessional) {
      setAnalyzingPremium(true);
    } else {
      setAnalyzing(true);
    }
    setError(null);
    try {
      // Use 'professional' parameter for business features, 'premium' for comprehensive UI analysis
      const urlParam = isProfessional ? 'professional=true' : 'premium=false';
      const response = await fetch(`http://localhost:8000/analyze-competitors?${urlParam}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        // Analysis complete, fetch recommendations
        await fetchRecommendations();
        setIsPremium(isProfessional);
        
        // Use setTimeout to ensure state updates complete before showing alert
        setTimeout(() => {
          const hasFeatures = features.length > 0;
          if (isProfessional) {
            alert('✨ Professional analysis completed! Business feature insights loaded.');
          } else if (hasFeatures) {
            alert('✅ Competitive analysis completed! Feature recommendations loaded.');
          } else {
            alert('✅ Analysis completed! No missing features found - your site is competitive!');
          }
        }, 100);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to run competitive analysis');
        alert('❌ Analysis failed: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Failed to trigger competitive analysis:', error);
      setError('Network error triggering analysis');
      alert('❌ Network error. Please try again.');
    } finally {
      setAnalyzing(false);
      setAnalyzingPremium(false);
    }
  };

  const handleSelectFeature = async (featureId: string) => {
    try {
      const response = await fetch('http://localhost:8000/select-feature', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature_id: featureId })
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedFeature(featureId);
        
        // Legacy callback
        if (onFeatureSelect) {
          onFeatureSelect(featureId);
        }
        
        // New chatbot integration
        if (data.success && data.session_id && onOpenChatbot) {
          console.log(`[FEATURE_SELECT] Opening chatbot with session ${data.session_id}`);
          onOpenChatbot(featureId, data.session_id);
        } else {
          // Fallback alert if no chatbot handler
          alert(`✅ Feature '${data.feature_name}' sent to chatbot for implementation!`);
        }
      }
    } catch (error) {
      console.error('Failed to select feature:', error);
      alert('❌ Failed to select feature. Please try again.');
    }
  };

  const getPriorityColor = (score: number) => {
    if (score >= 7) return 'bg-red-500';
    if (score >= 4) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  const getPriorityLabel = (score: number) => {
    if (score >= 7) return 'High Priority';
    if (score >= 4) return 'Medium Priority';
    return 'Low Priority';
  };

  if (loading) {
    return (
      <div className="glass-card rounded-xl p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        <p className="mt-4 text-gray-600">Loading feature recommendations...</p>
      </div>
    );
  }

  // Show success message if analysis ran but no features found
  if (!features || features.length === 0) {
    // Check if we have a summary (meaning analysis was run)
    if (summary && summary.total_competitors > 0) {
      return (
        <Card className="border-green-300 bg-gradient-to-br from-green-50 to-emerald-50 shadow-xl">
          <CardHeader>
            <CardTitle className="text-green-800 flex items-center gap-2">
              <span className="text-2xl">🎉</span> Great News!
            </CardTitle>
            <CardDescription>Your site is already competitive</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-green-900 mb-3">
              I analyzed <strong>{summary.total_competitors} competitor website{summary.total_competitors > 1 ? 's' : ''}</strong> and 
              found that your site already has all the key features they offer!
            </p>
            <p className="text-xs text-gray-600">
              No missing features were identified. Your site is doing well compared to competitors.
            </p>
          </CardContent>
        </Card>
      );
    }
    
    // No analysis run yet
    return (
      <Card className="glass-card rounded-xl shadow-xl">
        <CardHeader>
          <CardTitle className="text-gradient text-2xl">Feature Recommendations</CardTitle>
          <CardDescription>
            Analyze competitor websites to discover missing features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Discover what features your competitors have that you might be missing.
            </p>
            <div className="space-y-3">
              <Button
                onClick={() => triggerAnalysis(false)}
                disabled={analyzing || analyzingPremium}
                className="w-full gradient-button text-white font-semibold py-6 text-lg"
              >
                {analyzing ? '🔄 Analyzing Competitors...' : '🚀 Run Standard Analysis'}
              </Button>
              
              <Button
                onClick={() => triggerAnalysis(true)}
                disabled={analyzing || analyzingPremium}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-6 text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
              >
                {analyzingPremium ? '✨ Running Professional Analysis...' : '✨ Run Professional Analysis'}
              </Button>
            </div>
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-purple-200 rounded-lg p-4 mt-3">
              <p className="text-xs font-semibold text-purple-900 mb-2">ℹ️ Analysis Types:</p>
              <ul className="text-xs text-gray-700 space-y-1.5">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">•</span>
                  <span><strong className="text-blue-800">Standard:</strong> UI elements + SEO + Accessibility + Tech Stack detection</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-600 font-bold">•</span>
                  <span><strong className="text-purple-800">Professional:</strong> Business features (Payment methods, Delivery options, Reviews, COD, Try & Buy, Loyalty programs)</span>
                </li>
              </ul>
            </div>
            <p className="text-xs text-gray-500 text-center">
              ⏱️ Analysis takes 30-60 seconds. Make sure COMPETITOR_URLS is configured in .env
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="glass-card rounded-xl shadow-xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <CardTitle className="text-gradient text-2xl">Feature Recommendations</CardTitle>
              <CardDescription className="text-base">
                Based on analysis of {summary?.total_competitors || 0} competitor sites
              </CardDescription>
            </div>
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
        </CardHeader>
        <CardContent>
          {summary && (
            <div className="flex gap-3 mb-6">
              <Badge variant="destructive" className="px-4 py-2 text-sm">High: {summary.high_priority}</Badge>
              <Badge variant="default" className="px-4 py-2 text-sm bg-blue-600">Medium: {summary.medium_priority}</Badge>
              <Badge variant="secondary" className="px-4 py-2 text-sm">Low: {summary.low_priority}</Badge>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Natural Language Summary */}
      {isExpanded && summary && features.length > 0 && (
        <Card className="border-purple-300 bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50 shadow-xl">
          <CardContent className="pt-6">
            <div className="prose prose-sm max-w-none">
              <h3 className="text-xl font-bold text-gradient mb-3">📊 Analysis Summary</h3>
              <p className="text-gray-700 mb-3">
                I've analyzed <strong>{summary.total_competitors} competitor websites</strong> and compared them with your site. 
                Here's what I found:
              </p>
              
              <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4 mb-4 border border-purple-200 shadow-md">
                <p className="text-gray-800 mb-2">
                  <strong>Missing Features:</strong> Your competitors have <strong>{summary.total_gaps} features</strong> that 
                  your site doesn't currently have.
                </p>
                <ul className="list-none space-y-1.5 text-gray-700 ml-0">
                  <li className="flex items-start gap-2">
                    <span className="text-red-600 text-lg">•</span>
                    <span><strong>{summary.high_priority} high-priority</strong> features (found in most competitors)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 text-lg">•</span>
                    <span><strong>{summary.medium_priority} medium-priority</strong> features (found in some competitors)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-gray-600 text-lg">•</span>
                    <span><strong>{summary.low_priority} low-priority</strong> features (found in few competitors)</span>
                  </li>
                </ul>
              </div>

              <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-4 border border-purple-300 shadow-md">
                <p className="text-purple-900 font-bold mb-2 flex items-center gap-2">
                  <span className="text-xl">💡</span> What should I implement next?
                </p>
                <p className="text-gray-800 text-sm">
                  Review the feature cards below. Each one shows the priority score, how many competitors have it, 
                  estimated effort, and implementation notes. <strong className="text-purple-900">Click "Select for Implementation"</strong> on the 
                  feature you'd like me to work on next!
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {features.map((feature) => (
          <Card 
            key={feature.id} 
            className={`glass-card rounded-xl shadow-lg hover:shadow-2xl smooth-transition ${
              selectedFeature === feature.id ? 'border-2 border-green-500 bg-green-50/30' : 'hover:scale-[1.02]'
            }`}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    {feature.name}
                    <Badge className={`${getPriorityColor(feature.priority_score)} text-white shadow-md text-xs`}>
                      {getPriorityLabel(feature.priority_score)}
                    </Badge>
                  </CardTitle>
                  <CardDescription className="text-sm mt-1">{feature.description}</CardDescription>
                </div>
                <div className="text-right bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg p-2 ml-2">
                  <div className="text-2xl font-bold text-gradient">{feature.priority_score}/10</div>
                  <div className="text-xs text-gray-600">Priority</div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-purple-50 p-2 rounded-lg">
                  <span className="font-semibold text-purple-900 text-xs">Found in:</span>
                  <p className="text-gray-700 mt-1 text-xs">{feature.frequency_percentage}</p>
                  <p className="text-xs text-gray-500 mt-0.5 truncate">{feature.found_in.slice(0, 2).join(', ')}</p>
                </div>
                <div className="bg-blue-50 p-2 rounded-lg">
                  <span className="font-semibold text-blue-900 text-xs">Effort:</span>
                  <p className="text-gray-700 mt-1 text-xs">{feature.estimated_effort}</p>
                </div>
                <div className="bg-pink-50 p-2 rounded-lg">
                  <span className="font-semibold text-pink-900 text-xs">Complexity:</span>
                  <p className="text-gray-700 capitalize mt-1 text-xs">{feature.complexity}</p>
                </div>
                <div className="bg-green-50 p-2 rounded-lg">
                  <span className="font-semibold text-green-900 text-xs">Impact:</span>
                  <p className="text-gray-700 capitalize mt-1 text-xs">{feature.business_impact}</p>
                </div>
              </div>

              <div className="bg-gradient-to-r from-gray-50 to-purple-50 p-3 rounded-lg border border-purple-200">
                <p className="font-semibold mb-1 text-purple-900 text-xs">📝 Implementation Notes:</p>
                <p className="text-gray-700 text-xs line-clamp-2">{feature.implementation_notes}</p>
              </div>

              <Button
                onClick={() => handleSelectFeature(feature.id)}
                disabled={selectedFeature === feature.id}
                className={`w-full py-5 text-base font-semibold ${
                  selectedFeature === feature.id 
                    ? 'bg-green-600 hover:bg-green-700' 
                    : 'gradient-button'
                } text-white`}
                variant={selectedFeature === feature.id ? 'default' : 'default'}
              >
                {selectedFeature === feature.id ? '✓ Selected for Implementation' : 'Select for Implementation'}
              </Button>
            </CardContent>
          </Card>
          ))}
        </div>
      )}
    </div>
  );
}
