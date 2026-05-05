'use client';

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '@/lib/config';
import {
  Activity, CheckCircle, XCircle, AlertTriangle,
  Clock, GitBranch, Globe, Brain, Shield, Zap,
  ExternalLink, RefreshCw
} from 'lucide-react';

interface StatusMonitorProps {
  status?: any;
}

export function StatusMonitor({ status: propStatus }: StatusMonitorProps) {
  const [systemStatus, setSystemStatus] = useState<any>(propStatus || null);
  const [isLoading, setIsLoading] = useState(!propStatus);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    if (propStatus) {
      setSystemStatus(propStatus);
      setIsLoading(false);
      setLastUpdated(new Date());
    }
  }, [propStatus]);

  useEffect(() => {
    if (propStatus) return; // parent is polling
    const fetchStatus = async () => {
      try {
        const r = await fetch(`${API_BASE_URL}/status`);
        if (r.ok) { setSystemStatus(await r.json()); setLastUpdated(new Date()); }
      } catch {}
      finally { setIsLoading(false); }
    };
    fetchStatus();
    const iv = setInterval(fetchStatus, 8000);
    return () => clearInterval(iv);
  }, [propStatus]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-3">
        <RefreshCw className="h-6 w-6 text-zinc-600 animate-spin" />
        <span className="text-[10px] font-black uppercase tracking-widest text-zinc-600">Connecting…</span>
      </div>
    );
  }

  if (!systemStatus) {
    return (
      <div className="flex flex-col items-center py-10 gap-3 text-center">
        <XCircle className="h-8 w-8 text-red-500/60" />
        <p className="text-xs font-bold uppercase tracking-widest text-zinc-500">Engine Offline</p>
        <p className="text-[10px] text-zinc-700">Make sure the backend is running on port 8000</p>
      </div>
    );
  }

  const h = systemStatus.health || {};
  const env = systemStatus.environment || {};
  const isHealthy = h.status === 'healthy';
  const isDegraded = h.status === 'degraded';

  const statusCfg = isHealthy
    ? { label: 'Healthy', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20', dot: 'bg-emerald-400' }
    : isDegraded
    ? { label: 'Degraded', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20', dot: 'bg-amber-400' }
    : { label: h.status || 'Unknown', color: 'text-zinc-400', bg: 'bg-zinc-500/10 border-zinc-500/20', dot: 'bg-zinc-400' };

  const safetyFeatures = h.safety_features || {};

  return (
    <div className="space-y-5">
      {/* Status pill + version */}
      <div className="flex items-center justify-between">
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${statusCfg.bg}`}>
          <span className={`w-2 h-2 rounded-full ${statusCfg.dot} ${isHealthy ? 'animate-pulse' : ''}`} />
          <span className={`text-[10px] font-black uppercase tracking-widest ${statusCfg.color}`}>
            {statusCfg.label}
          </span>
        </div>
        <span className="text-[10px] text-zinc-700 tabular-nums">
          v{h.version || '1.0'} · {lastUpdated ? lastUpdated.toLocaleTimeString() : '—'}
        </span>
      </div>

      {/* Key metrics as mini-table */}
      <div className="space-y-2.5">
        {[
          {
            icon: <Clock className="h-3.5 w-3.5" />,
            label: 'Last Run',
            value: h.last_run ? new Date(h.last_run).toLocaleTimeString() : '—',
          },
          {
            icon: <Globe className="h-3.5 w-3.5" />,
            label: 'Website',
            value: env.website_url ? new URL(env.website_url).hostname : 'Not configured',
            truncate: true,
          },
          {
            icon: <GitBranch className="h-3.5 w-3.5" />,
            label: 'Repository',
            value: env.github_repo || 'Not configured',
            truncate: true,
          },
          {
            icon: <Brain className="h-3.5 w-3.5" />,
            label: 'Monitoring Mode',
            value: env.monitoring_mode || 'N/A',
          },
        ].map((item, i) => (
          <div key={i} className="flex items-center justify-between py-2 border-b border-white/[0.04] last:border-0">
            <div className="flex items-center gap-2 text-zinc-600 min-w-0">
              {item.icon}
              <span className="text-[11px] text-zinc-500 font-medium whitespace-nowrap">{item.label}</span>
            </div>
            <span className={`text-[11px] text-zinc-300 font-medium ml-2 ${item.truncate ? 'truncate max-w-[130px]' : ''}`}>
              {item.value}
            </span>
          </div>
        ))}
      </div>

      {/* Safety flags */}
      <div>
        <p className="text-[9px] font-black uppercase tracking-[0.3em] text-zinc-700 mb-3">Safety Guardrails</p>
        <div className="grid grid-cols-2 gap-2">
          {[
            { label: 'Validation', on: safetyFeatures.validation_enabled !== false },
            { label: 'Rollback', on: safetyFeatures.rollback_enabled !== false },
            { label: 'Fix Testing', on: env.test_fixes_before_apply !== false },
            { label: 'Improved Fixer', on: !!env.use_improved_fixer },
          ].map((f, i) => (
            <div key={i} className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
              f.on ? 'bg-emerald-500/5 border-emerald-500/15' : 'bg-white/[0.02] border-white/[0.04]'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${f.on ? 'bg-emerald-400' : 'bg-zinc-600'}`} />
              <span className={`text-[10px] font-medium ${f.on ? 'text-emerald-400' : 'text-zinc-600'}`}>{f.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent events */}
      {(h.last_pr || h.last_error) && (
        <div>
          <p className="text-[9px] font-black uppercase tracking-[0.3em] text-zinc-700 mb-3">Recent Events</p>
          <div className="space-y-2">
            {h.last_pr && (
              <a
                href={h.last_pr}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02] border border-white/[0.05] hover:bg-white/[0.05] transition-colors group"
              >
                <div className="flex items-center gap-2 text-zinc-400">
                  <GitBranch className="h-3.5 w-3.5" />
                  <span className="text-[11px] font-medium">Latest PR</span>
                </div>
                <ExternalLink className="h-3 w-3 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
              </a>
            )}
            {h.last_error && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                <XCircle className="h-3.5 w-3.5 text-red-400 flex-shrink-0 mt-0.5" />
                <span className="text-[10px] text-red-400/80 leading-relaxed line-clamp-2">{h.last_error}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
