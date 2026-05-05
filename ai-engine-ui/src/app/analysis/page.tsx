'use client';

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '@/lib/config';
import { ConfigurationForm } from '@/components/ConfigurationForm';
import { StatusMonitor } from '@/components/StatusMonitor';
import FeatureImplementationStatus from '@/components/FeatureImplementationStatus';
import FeatureRecommendations from '@/components/FeatureRecommendations';
import { ChatWidget } from '@/components/ChatWidget';
import { TaskQueue } from '@/components/TaskQueue';
import { Notifications } from '@/components/Notifications';
import { AnimatedSection } from '@/components/shared/AnimatedSection';
import {
  Settings, Activity, ListChecks, Bell, Zap,
  TrendingUp, Shield, RefreshCw, CheckCircle2,
  AlertTriangle, Clock, GitBranch, Globe, Brain,
  ChevronRight, ArrowUpRight, Cpu, Database, Trash2
} from 'lucide-react';

interface MetricCard {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  color?: string;
}

export default function AnalysisPage() {
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [lastRunAge, setLastRunAge] = useState('—');

  useEffect(() => {
    fetchStatus();
    fetchTasks();
    const statusInterval = setInterval(fetchStatus, 10000);
    const taskInterval = setInterval(fetchTasks, 8000);
    return () => {
      clearInterval(statusInterval);
      clearInterval(taskInterval);
    };
  }, []);

  // Compute "last run age" from systemStatus
  useEffect(() => {
    if (!systemStatus?.health?.last_run) { setLastRunAge('Never'); return; }
    const diff = Date.now() - new Date(systemStatus.health.last_run).getTime();
    const mins = Math.floor(diff / 60000);
    const hrs = Math.floor(mins / 60);
    if (hrs > 0) setLastRunAge(`${hrs}h ${mins % 60}m ago`);
    else if (mins > 0) setLastRunAge(`${mins}m ago`);
    else setLastRunAge('Just now');
  }, [systemStatus]);

  const fetchStatus = async () => {
    try {
      const r = await fetch(`${API_BASE_URL}/status`);
      if (r.ok) setSystemStatus(await r.json());
    } catch {}
  };

  const fetchTasks = async () => {
    try {
      const r = await fetch(`${API_BASE_URL}/tasks`);
      if (r.ok) { const d = await r.json(); setTasks(d.tasks || []); }
    } catch {}
  };

  const [activeTab, setActiveTab] = useState<'notifications' | 'queue'>('notifications');

  const triggerCycle = async () => {
    setIsRunning(true);
    try {
      await fetch(`${API_BASE_URL}/run`, { method: 'POST' });
      setTimeout(fetchStatus, 2000);
    } catch {}
    setTimeout(() => setIsRunning(false), 4000);
  };

  const clearAllNotifications = async () => {
    if (!confirm('Clear all system alerts?')) return;
    try {
      await fetch(`${API_BASE_URL}/notifications`, { method: 'DELETE' });
      fetchStatus(); // Refresh status
    } catch {}
  };

  const health = systemStatus?.health || {};
  const env = systemStatus?.environment || {};
  const bugsDetected = health.bugs_detected ?? '—';
  const bugsQueued = health.bugs_queued ?? '—';
  const isHealthy = health.status === 'healthy';
  const activeTasks = tasks.filter(t => !t.ready).length;
  const completedTasks = tasks.filter(t => t.ready && t.status === 'SUCCESS').length;

  const metrics: MetricCard[] = [
    {
      label: 'Engine Status',
      value: isHealthy ? 'Healthy' : health.status || 'Unknown',
      sub: 'System health',
      icon: <Shield className="h-5 w-5" />,
      color: isHealthy ? 'text-emerald-400' : 'text-amber-400',
    },
    {
      label: 'Bugs Detected',
      value: bugsDetected,
      sub: 'Last cycle',
      icon: <AlertTriangle className="h-5 w-5" />,
      color: 'text-zinc-300',
    },
    {
      label: 'Queued Fixes',
      value: bugsQueued,
      sub: 'In pipeline',
      icon: <Database className="h-5 w-5" />,
      color: 'text-zinc-300',
    },
    {
      label: 'Active Tasks',
      value: activeTasks,
      sub: `${completedTasks} completed`,
      icon: <Cpu className="h-5 w-5" />,
      color: activeTasks > 0 ? 'text-sky-400' : 'text-zinc-300',
    },
    {
      label: 'Last Cycle',
      value: lastRunAge,
      sub: 'Maintenance run',
      icon: <Clock className="h-5 w-5" />,
      color: 'text-zinc-400',
    },
    {
      label: 'Environment',
      value: env.environment || 'Development',
      sub: env.website_url ? new URL(env.website_url).hostname : 'Not configured',
      icon: <Globe className="h-5 w-5" />,
      color: 'text-zinc-400',
    },
  ];

  return (
    <div className="bg-black min-h-screen pt-28 pb-24 px-4 overflow-hidden relative">
      {/* Background ambient glows */}
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-white/[0.02] rounded-full blur-[180px] -mr-80 -mt-80 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-white/[0.015] rounded-full blur-[120px] -ml-40 pointer-events-none" />

      <div className="max-w-[1400px] mx-auto relative z-10">

        {/* ── PAGE HEADER ─────────────────────────────── */}
        <AnimatedSection>
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-16">
            <div>
              <p className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-600 mb-3">
                AI Engine · Intelligence Hub
              </p>
              <h1 className="text-5xl md:text-7xl font-bold uppercase tracking-tighter text-white leading-none mb-3">
                Core <span className="text-zinc-500 italic">Intelligence</span>
              </h1>
              <p className="text-base text-zinc-500 font-light max-w-xl">
                Autonomous heuristics · Fix pipelines · Real-time monitoring
              </p>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center space-x-2 px-6 py-3 bg-white/5 border border-white/10 rounded-2xl">
                <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse' : 'bg-amber-500'}`} />
                <span className="text-[10px] font-black uppercase tracking-widest text-zinc-400">
                  {isHealthy ? 'Engine Online' : 'Degraded Mode'}
                </span>
              </div>
              <button
                onClick={triggerCycle}
                disabled={isRunning}
                className="flex items-center gap-3 px-8 py-4 bg-white text-black text-[10px] font-black uppercase tracking-[0.2em] rounded-full hover:bg-zinc-200 active:scale-95 transition-all disabled:opacity-50 shadow-[0_0_30px_-5px_rgba(255,255,255,0.3)]"
              >
                <RefreshCw className={`h-4 w-4 ${isRunning ? 'animate-spin' : ''}`} />
                {isRunning ? 'Analyzing…' : 'Start Cycle'}
              </button>
            </div>
          </div>
        </AnimatedSection>

        {/* ── METRICS ROW ─────────────────────────────── */}
        <AnimatedSection delay={0.05}>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
            {metrics.map((m, i) => (
              <div
                key={i}
                className="premium-card p-6 flex flex-col gap-4 hover:bg-white/[0.04] transition-all hover:-translate-y-1 group"
              >
                <div className="flex items-center justify-between">
                  <div className={`p-2 rounded-xl bg-white/[0.03] border border-white/5 ${m.color} group-hover:border-white/20 transition-all`}>
                    {m.icon}
                  </div>
                  <ArrowUpRight className="h-3.5 w-3.5 text-zinc-800 group-hover:text-zinc-500 transition-colors" />
                </div>
                <div>
                  <p className={`text-2xl font-bold tabular-nums tracking-tighter ${m.color}`}>{m.value}</p>
                  <p className="text-[9px] font-black uppercase tracking-widest text-zinc-600 mt-1">{m.label}</p>
                </div>
              </div>
            ))}
          </div>
        </AnimatedSection>

        {/* ── TOP ROW: SYSTEM MONITORING ───────────────── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Integration Health / System Gateways */}
          <AnimatedSection delay={0.1}>
            <div className="premium-card p-8 h-full">
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-600 mb-8 pb-4 border-b border-white/5">System Gateways</p>
              <div className="space-y-4">
                {[
                  { label: 'Gemini API', ok: env.has_gemini_token, icon: <Brain className="h-4 w-4" /> },
                  { label: 'GitHub Token', ok: env.has_github_token, icon: <GitBranch className="h-4 w-4" /> },
                  { label: 'Analytics', ok: env.has_ga_credentials, icon: <TrendingUp className="h-4 w-4" /> },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between py-1 group">
                    <div className="flex items-center gap-4 text-zinc-400 group-hover:text-zinc-200 transition-colors">
                      <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center border border-white/5 group-hover:border-white/10 transition-all">
                        {item.icon}
                      </div>
                      <span className="text-[10px] font-bold uppercase tracking-tight">{item.label}</span>
                    </div>
                    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-[8px] font-black uppercase tracking-widest ${
                      item.ok
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-zinc-900 text-zinc-700 border border-white/5'
                    }`}>
                      {item.ok ? 'Online' : 'Offline'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </AnimatedSection>

          {/* Notifications & Queue System */}
          <AnimatedSection delay={0.15}>
            <div className="premium-card h-full overflow-hidden flex flex-col">
              <div className="flex border-b border-white/5 relative">
                <button 
                  onClick={() => setActiveTab('notifications')}
                  className={`flex-1 px-6 py-4 text-[9px] font-black uppercase tracking-[0.2em] transition-all ${activeTab === 'notifications' ? 'text-white' : 'text-zinc-600'}`}
                >
                  Alerts
                </button>
                <button 
                  onClick={() => setActiveTab('queue')}
                  className={`flex-1 px-6 py-4 text-[9px] font-black uppercase tracking-[0.2em] transition-all ${activeTab === 'queue' ? 'text-white' : 'text-zinc-600'}`}
                >
                  Queue ({activeTasks})
                </button>
                {/* Underline indicator */}
                <div 
                  className="absolute bottom-0 h-0.5 bg-white transition-all duration-300" 
                  style={{ 
                    width: '50%', 
                    left: activeTab === 'notifications' ? '0%' : '50%' 
                  }} 
                />
              </div>

              <div className="p-6 max-h-[160px] overflow-y-auto custom-scrollbar flex-1">
                {activeTab === 'notifications' ? (
                  <>
                    <div className="flex justify-end mb-4">
                      <button 
                        onClick={clearAllNotifications}
                        className="text-[8px] font-black uppercase tracking-widest text-zinc-700 hover:text-white transition-colors flex items-center gap-1.5"
                      >
                        <Trash2 className="h-2.5 w-2.5" />
                        Clear Alerts
                      </button>
                    </div>
                    <Notifications />
                  </>
                ) : (
                  <TaskQueue />
                )}
              </div>
            </div>
          </AnimatedSection>

          {/* Quick Actions / Heuristic Access */}
          <AnimatedSection delay={0.2}>
            <div className="premium-card p-8 h-full">
              <p className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-600 mb-8 pb-4 border-b border-white/5">Heuristic Access</p>
              <div className="space-y-2">
                {[
                  { label: 'Bug Review', action: () => window.location.href = '/bugs', icon: <AlertTriangle className="h-4 w-4" /> },
                  { label: 'Feature Request', action: () => window.location.href = '/features', icon: <Zap className="h-4 w-4" /> },
                  { label: 'System Sync', action: triggerCycle, icon: <RefreshCw className="h-4 w-4" />, loading: isRunning },
                ].map((a, i) => (
                  <button
                    key={i}
                    onClick={a.action}
                    disabled={a.loading}
                    className="w-full flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5 hover:bg-white text-white hover:text-black transition-all group disabled:opacity-50"
                  >
                    <div className="flex items-center gap-4">
                      <span className={a.loading ? 'animate-spin' : ''}>{a.icon}</span>
                      <span className="text-[9px] font-black uppercase tracking-widest">{a.label}</span>
                    </div>
                    <ChevronRight className="h-3 w-3 opacity-30 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            </div>
          </AnimatedSection>
        </div>

        {/* ── SECOND ROW: CORE CONTROLS ────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* System Configuration / Config Core */}
          <AnimatedSection delay={0.25}>
            <div className="premium-card p-8 h-full">
              <div className="flex items-center justify-between mb-8 pb-4 border-b border-white/5">
                <div className="flex items-center space-x-3">
                  <Settings className="h-4 w-4 text-zinc-500" />
                  <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-white">Config Core</h2>
                </div>
              </div>
              <ConfigurationForm
                onConfigured={(config) => console.log(config)}
                onStatusUpdate={() => {}}
              />
            </div>
          </AnimatedSection>

          {/* Engine Vitals */}
          <AnimatedSection delay={0.3}>
            <div className="premium-card p-8 h-full">
              <div className="flex items-center justify-between mb-8 pb-4 border-b border-white/5">
                <div className="flex items-center space-x-3">
                  <Activity className="h-4 w-4 text-zinc-500" />
                  <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-white">Engine Vitals</h2>
                </div>
              </div>
              <StatusMonitor status={systemStatus} />
            </div>
          </AnimatedSection>
        </div>

        {/* ── THIRD ROW: PROJECT PROGRESS ─────────────── */}
        <div className="space-y-8 mt-12">
          <AnimatedSection delay={0.35}>
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-6">
                <ListChecks className="h-4 w-4 text-zinc-500" />
                <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-white">Project Modules</h2>
                <div className="flex-1 h-px bg-white/5" />
              </div>
              <FeatureImplementationStatus />
            </div>
          </AnimatedSection>

          <AnimatedSection delay={0.4}>
            <div>
              <div className="flex items-center gap-3 mb-6">
                <TrendingUp className="h-4 w-4 text-zinc-500" />
                <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-white">Competitive Intelligence</h2>
                <div className="flex-1 h-px bg-white/5" />
              </div>
              <FeatureRecommendations />
            </div>
          </AnimatedSection>
        </div>
      </div>

      <ChatWidget />
    </div>
  );
}
