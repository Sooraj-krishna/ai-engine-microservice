'use client';

import { useState, useEffect } from 'react';
import { ConfigurationForm } from '@/components/ConfigurationForm';
import { LogsDisplay } from '@/components/LogsDisplay';
import { StatusMonitor } from '@/components/StatusMonitor';
import { Header } from '@/components/Header';
import { IdentifiedBugs } from '@/components/IdentifiedBugs';
import FeatureRecommendations from '@/components/FeatureRecommendations';
import FeatureImplementationStatus from '@/components/FeatureImplementationStatus';
import { ChatWidget } from '@/components/ChatWidget';

export default function Home() {
  const [isConfigured, setIsConfigured] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/logs');

    ws.onopen = () => {
      console.log('WebSocket connection established');
      setLogs(prevLogs => [...prevLogs, '[INFO] WebSocket connection established.']);
    };

    ws.onmessage = (event) => {
      setLogs(prevLogs => [...prevLogs, event.data]);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      setLogs(prevLogs => [...prevLogs, '[INFO] WebSocket connection closed.']);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setLogs(prevLogs => [...prevLogs, `[ERROR] WebSocket error: ${error}`]);
    };

    // Cleanup on component unmount
    return () => {
      ws.close();
    };
  }, []); // Empty dependency array means this effect runs once on mount


  return (
    <div className="min-h-screen">
      <Header />
      
      <main className="container mx-auto px-4 py-8 space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Configuration Panel */}
          <div className="glass-card rounded-xl p-6 smooth-transition hover:shadow-2xl">
            <h2 className="text-2xl font-bold text-gradient mb-4">
              AI Engine Configuration
            </h2>
            <ConfigurationForm 
              onConfigured={setIsConfigured}
              onStatusUpdate={setSystemStatus}
            />
          </div>

          {/* Status Monitor */}
          <div className="glass-card rounded-xl p-6 smooth-transition hover:shadow-2xl">
            <h2 className="text-2xl font-bold text-gradient mb-4">
              System Status
            </h2>
            <StatusMonitor status={systemStatus} />
          </div>
        </div>

        {/* Identified Bugs */}
        <IdentifiedBugs issues={systemStatus?.issues || []} />

        {/* Feature Implementation Status */}
        <FeatureImplementationStatus />

        {/* Feature Recommendations - Competitive Analysis */}
        <FeatureRecommendations />

        {/* Logs Display */}
        <div className="glass-card rounded-xl p-6 smooth-transition hover:shadow-2xl">
          <h2 className="text-2xl font-bold text-gradient mb-4">
            Real-time Logs
          </h2>
          <LogsDisplay logs={logs} />
        </div>
      </main>

      {/* AI Chatbot Widget */}
      <ChatWidget />
    </div>
  );
}
