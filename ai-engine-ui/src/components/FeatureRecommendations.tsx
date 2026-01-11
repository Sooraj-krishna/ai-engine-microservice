/**
 * Feature Recommendations Component
 * Displays competitive analysis results and allows feature selection
 */

'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

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
}

export default function FeatureRecommendations({ onFeatureSelect }: FeatureRecommendationsProps) {
  const [features, setFeatures] = useState<Feature[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzingPremium, setAnalyzingPremium] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPremium, setIsPremium] = useState(false);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/feature-recommendations');
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
      setError('Network error fetching recommendations');
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
        setSelectedFeature(featureId);
        if (onFeatureSelect) {
          onFeatureSelect(featureId);
        }
        alert('Feature selected for future implementation!');
      }
    } catch (error) {
      console.error('Failed to select feature:', error);
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
    return <div className="p-6 text-center">Loading feature recommendations...</div>;
  }

  // Show success message if analysis ran but no features found
  if (!features || features.length === 0) {
    // Check if we have a summary (meaning analysis was run)
    if (summary && summary.total_competitors > 0) {
      return (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-800">🎉 Great News!</CardTitle>
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
      <Card>
        <CardHeader>
          <CardTitle>Feature Recommendations</CardTitle>
          <CardDescription>
            {error ? 'No competitive analysis available yet' : 'No competitive analysis results available'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {error && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">{error}</p>
              </div>
            )}
            <p className="text-sm text-gray-600">
              Analyze competitor websites to discover missing features and improvement opportunities.
            </p>
            <div className="space-y-3">
              <Button
                onClick={() => triggerAnalysis(false)}
                disabled={analyzing || analyzingPremium}
                className="w-full"
              >
                {analyzing ? '🔄 Analyzing Competitors...' : '🚀 Run Standard Analysis'}
              </Button>
              
              <Button
                onClick={() => triggerAnalysis(true)}
                disabled={analyzing || analyzingPremium}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
              >
                {analyzingPremium ? '✨ Running Professional Analysis...' : '✨ Run Professional Analysis'}
              </Button>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-3">
              <p className="text-xs font-semibold text-blue-900 mb-1">ℹ️ Analysis Types:</p>
              <ul className="text-xs text-blue-800 space-y-1">
                <li><strong>Standard:</strong> UI elements + SEO + Accessibility + Tech Stack detection</li>
                <li><strong>Professional:</strong> Business features (Payment methods, Delivery options, Reviews, COD, Try & Buy, Loyalty programs)</li>
              </ul>
            </div>
            <p className="text-xs text-gray-500">
              Note: Analysis takes 30-60 seconds. Make sure COMPETITOR_URLS is configured in .env
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Feature Recommendations</CardTitle>
          <CardDescription>
            Based on analysis of {summary?.total_competitors || 0} competitor sites
          </CardDescription>
        </CardHeader>
        <CardContent>
          {summary && (
            <div className="flex gap-4 mb-6">
              <Badge variant="destructive">High: {summary.high_priority}</Badge>
              <Badge variant="default">Medium: {summary.medium_priority}</Badge>
              <Badge variant="secondary">Low: {summary.low_priority}</Badge>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Natural Language Summary */}
      {summary && features.length > 0 && (
        <Card className="mt-4 border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="prose prose-sm max-w-none">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">📊 Analysis Summary</h3>
              <p className="text-gray-700 mb-3">
                I've analyzed <strong>{summary.total_competitors} competitor websites</strong> and compared them with your site. 
                Here's what I found:
              </p>
              
              <div className="bg-white rounded-lg p-4 mb-4 border border-blue-200">
                <p className="text-gray-800 mb-2">
                  <strong>Missing Features:</strong> Your competitors have <strong>{summary.total_gaps} features</strong> that 
                  your site doesn't currently have.
                </p>
                <ul className="list-disc list-inside space-y-1 text-gray-700 ml-2">
                  <li><strong>{summary.high_priority} high-priority</strong> features (found in most competitors)</li>
                  <li><strong>{summary.medium_priority} medium-priority</strong> features (found in some competitors)</li>
                  <li><strong>{summary.low_priority} low-priority</strong> features (found in few competitors)</li>
                </ul>
              </div>

              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
                <p className="text-purple-900 font-semibold mb-2">💡 What should I implement next?</p>
                <p className="text-gray-700 text-sm">
                  Review the feature cards below. Each one shows the priority score, how many competitors have it, 
                  estimated effort, and implementation notes. <strong>Click "Select for Implementation"</strong> on the 
                  feature you'd like me to work on next!
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {features.map((feature) => (
        <Card key={feature.id} className={selectedFeature === feature.id ? 'border-green-500 border-2' : ''}>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="flex items-center gap-2">
                  {feature.name}
                  <Badge className={getPriorityColor(feature.priority_score)}>
                    {getPriorityLabel(feature.priority_score)}
                  </Badge>
                </CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold">{feature.priority_score}/10</div>
                <div className="text-xs text-gray-500">Priority Score</div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-semibold">Found in:</span>
                  <p className="text-gray-600">{feature.frequency_percentage} of competitors</p>
                  <p className="text-xs text-gray-500">{feature.found_in.join(', ')}</p>
                </div>
                <div>
                  <span className="font-semibold">Effort:</span>
                  <p className="text-gray-600">{feature.estimated_effort}</p>
                </div>
                <div>
                  <span className="font-semibold">Complexity:</span>
                  <p className="text-gray-600 capitalize">{feature.complexity}</p>
                </div>
                <div>
                  <span className="font-semibold">Business Impact:</span>
                  <p className="text-gray-600 capitalize">{feature.business_impact}</p>
                </div>
              </div>

              <div className="bg-gray-50 p-3 rounded text-sm">
                <p className="font-semibold mb-1">Implementation Notes:</p>
                <p className="text-gray-700">{feature.implementation_notes}</p>
              </div>

              <Button
                onClick={() => handleSelectFeature(feature.id)}
                disabled={selectedFeature === feature.id}
                className="w-full"
                variant={selectedFeature === feature.id ? 'outline' : 'default'}
              >
                {selectedFeature === feature.id ? '✓ Selected for Implementation' : 'Select for Implementation'}
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
