'use client';

import { useState, useEffect } from 'react';
import { ConfigurationForm } from '@/components/ConfigurationForm';
import { StatusMonitor } from '@/components/StatusMonitor';
import { LogsDisplay } from '@/components/LogsDisplay';
import FeatureImplementationStatus from '@/components/FeatureImplementationStatus';
import FeatureRecommendations from '@/components/FeatureRecommendations';
import { ChatWidget } from '@/components/ChatWidget';
import { AnimatedSection } from '@/components/shared/AnimatedSection';

export default function AnalysisPage() {
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [features, setFeatures] = useState<any[]>([]);

  useEffect(() => {
    // Fetch initial status
    fetchStatus();
    
    // Poll for updates
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection for real-time logs
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket('ws://localhost:8000/ws/logs');
        
        ws.onopen = () => {
          console.log('[WebSocket] Connected to log stream');
        };
        
        ws.onmessage = (event) => {
          try {
            // Try parsing as JSON first (for future compatibility)
            const data = JSON.parse(event.data);
            if (data.log) {
              setLogs(prev => [...prev, data.log]);
            } else if (data.message) {
              setLogs(prev => [...prev, data.message]);
            }
          } catch (error) {
            // Not JSON, treat as plain text log message
            if (event.data && typeof event.data === 'string' && event.data.trim()) {
              setLogs(prev => [...prev, event.data]);
            }
          }
        };
        
        ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
        };
        
        ws.onclose = () => {
          console.log('[WebSocket] Disconnected. Reconnecting in 5 seconds...');
          reconnectTimeout = setTimeout(connectWebSocket, 5000);
        };
      } catch (error) {
        console.error('[WebSocket] Connection failed:', error);
        reconnectTimeout = setTimeout(connectWebSocket, 5000);
      }
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
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
            <p className="text-xl text-zinc-400">
              Monitor, analyze, and maintain your codebase in real-time
            </p>
          </div>
        </AnimatedSection>
      </div>

      <main className="max-w-7xl mx-auto space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Configuration Panel */}
          <AnimatedSection delay={0.1}>
            <div className="dark-card rounded-lg p-6 smooth-transition hover:border-cyan-700/50">
              <h2 className="text-2xl font-bold text-red-gradient mb-4 uppercase tracking-wide">
                AI Engine Configuration
              </h2>
              <ConfigurationForm
                onConfigured={handleConfigured}
                onStatusUpdate={(status) => handleStatusUpdate('Status updated', 'info')}
              />
            </div>
          </AnimatedSection>

          {/* Status Monitor */}
          <AnimatedSection delay={0.2}>
            <div className="dark-card rounded-lg p-6 smooth-transition hover:border-cyan-700/50">
              <h2 className="text-2xl font-bold text-red-gradient mb-4 uppercase tracking-wide">
                System Status
              </h2>
              <StatusMonitor status={systemStatus} />
            </div>
          </AnimatedSection>
        </div>

        {/* Real-time Logs */}
        <AnimatedSection delay={0.3}>
          <div className="dark-card rounded-lg p-6 smooth-transition hover:border-cyan-700/50">
            <h2 className="text-2xl font-bold text-red-gradient mb-4 uppercase tracking-wide">
              Real-Time Logs
            </h2>
            <LogsDisplay logs={logs} />
          </div>
        </AnimatedSection>

        {/* Feature Implementation Status */}
        <AnimatedSection delay={0.4}>
          <div className="dark-card rounded-lg p-6 smooth-transition hover:border-cyan-700/50">
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
