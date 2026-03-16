'use client';

import { useState, useEffect } from 'react';
import { ConfigurationForm } from '@/components/ConfigurationForm';
import { StatusMonitor } from '@/components/StatusMonitor';

import FeatureImplementationStatus from '@/components/FeatureImplementationStatus';
import FeatureRecommendations from '@/components/FeatureRecommendations';
import { ChatWidget } from '@/components/ChatWidget';
import { TaskQueue } from '@/components/TaskQueue';
import { Notifications } from '@/components/Notifications';
import { AnimatedSection } from '@/components/shared/AnimatedSection';

export default function AnalysisPage() {
  const [systemStatus, setSystemStatus] = useState<any>(null);

  const [features, setFeatures] = useState<any[]>([]);

  useEffect(() => {
    // Fetch initial status
    fetchStatus();
    
    // Poll for updates
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);



  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/status');
      if (response.ok) {
        const data = await response.json();
        setSystemStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  };

  const handleConfigured = (config: any) => {
    console.log('Configuration updated:', config);
  };

  const handleStatusUpdate = (message: string, status: 'success' | 'error' | 'info') => {
    console.log(`[${status}] ${message}`);
  };

  return (
    <div className="page-enter min-h-screen py-24 px-4">
      {/* Page Header */}
      <div className="max-w-7xl mx-auto mb-12">
        <AnimatedSection>
          <div className="text-center mb-8">
            <h1 className="text-5xl md:text-6xl font-bold uppercase tracking-wider text-white mb-4">
              AI Engine <span className="text-red-gradient">Dashboard</span>
            </h1>
            <p className="text-xl text-white/50">
              Monitor, analyze, and maintain your codebase in real-time
            </p>
          </div>
        </AnimatedSection>
      </div>

      <main className="max-w-7xl mx-auto space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          {/* Column 1: Config & Notifications */}
          <div className="space-y-8">
            <AnimatedSection delay={0.1}>
              <div className="dark-card p-6 smooth-transition">
                <h2 className="text-2xl font-bold text-red-gradient mb-4 uppercase tracking-wide">
                  AI Engine Configuration
                </h2>
                <ConfigurationForm
                  onConfigured={handleConfigured}
                  onStatusUpdate={(status) => handleStatusUpdate('Status updated', 'info')}
                />
              </div>
            </AnimatedSection>

            <AnimatedSection delay={0.22}>
              <div className="dark-card p-6 smooth-transition">
                <Notifications />
              </div>
            </AnimatedSection>
          </div>

          {/* Column 2: Status & Task Queue */}
          <div className="space-y-8">
            <AnimatedSection delay={0.2}>
              <div className="dark-card p-6 smooth-transition">
                <h2 className="text-2xl font-bold text-red-gradient mb-4 uppercase tracking-wide">
                  System Status
                </h2>
                <StatusMonitor status={systemStatus} />
              </div>
            </AnimatedSection>

            <AnimatedSection delay={0.25}>
              <div className="dark-card p-6 smooth-transition">
                <h2 className="text-2xl font-bold text-red-gradient mb-4 uppercase tracking-wide">
                  Background Task Queue
                </h2>
                <TaskQueue />
              </div>
            </AnimatedSection>
          </div>
        </div>



        {/* Feature Implementation Status */}
        <AnimatedSection delay={0.4}>
          <div className="dark-card p-6 smooth-transition">
            <h2 className="text-2xl font-bold text-red-gradient mb-4 uppercase tracking-wide">
              Feature Implementation Status
            </h2>
            <FeatureImplementationStatus />
          </div>
        </AnimatedSection>

        {/* Feature Recommendations - Full Width */}
        <AnimatedSection delay={0.5}>
          <FeatureRecommendations />
        </AnimatedSection>
      </main>

      {/* Chat Widget */}
      <ChatWidget />
    </div>
  );
}
