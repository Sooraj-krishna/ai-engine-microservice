'use client';

import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '@/lib/config';
import { CheckCircle2, Clock, Loader2, ExternalLink, ShieldCheck } from 'lucide-react';

interface BugProgress {
  bug_id: string;
  severity: string;
  status: string;
  bug: {
    type: string;
    description: string;
  };
  progress: {
    stage: string;
    percentage: number;
    current_step: string;
    pr_url?: string;
    started_at?: string;
    stages: {
      plan_generation: StageStatus;
      validation: StageStatus;
      execution: StageStatus;
      git_push: StageStatus;
    };
  };
}

interface StageStatus {
  status: 'pending' | 'in_progress' | 'completed';
  started_at?: string;
  completed_at?: string;
}

interface Props {
  bugId: string;
  refreshInterval?: number;
}

const BugProgressTracker: React.FC<Props> = ({ bugId, refreshInterval = 2000 }) => {
  const [progress, setProgress] = useState<BugProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProgress();
    const interval = setInterval(fetchProgress, refreshInterval);
    return () => clearInterval(interval);
  }, [bugId, refreshInterval]);

  const fetchProgress = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/bugs/${bugId}/progress`);
      if (!response.ok) throw new Error('Failed to fetch progress');
      const data = await response.json();
      setProgress(data);
      setError(null);
      setLoading(false);
    } catch (err) {
      setError('Failed to load progress');
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-zinc-600 animate-pulse uppercase tracking-[0.3em] text-[10px] font-black">Connecting...</div>;
  if (error || !progress || !progress.progress || !progress.progress.stages) return null;

  const stages = [
    { key: 'plan_generation', label: 'Architecture Analysis' },
    { key: 'validation', label: 'Fix Synthesis' },
    { key: 'execution', label: 'Byte-Code Injection' },
    { key: 'git_push', label: 'Synchronization' }
  ];

  return (
    <div className="p-8 bg-black/40 backdrop-blur-2xl border border-white/5 rounded-2xl">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center space-x-3">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
          <h3 className="text-white font-bold uppercase tracking-tighter text-sm">
            Operational Logic: {progress.bug.type?.replace(/_/g, ' ')}
          </h3>
        </div>
        <div className="text-2xl font-black text-white tracking-tighter italic">
          {progress.progress?.percentage || 0}%
        </div>
      </div>

      <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden mb-10">
        <div 
          className="h-full bg-white shadow-[0_0_20px_rgba(255,255,255,0.5)] transition-all duration-1000 ease-out" 
          style={{ width: `${progress.progress?.percentage || 0}%` }}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
        {stages.map(stage => {
          const stageStatus = progress.progress?.stages?.[stage.key as keyof typeof progress.progress.stages] || 
                              { status: 'pending' as const };
          
          return (
            <div key={stage.key} className={`p-4 rounded-xl border transition-all duration-500 ${
              stageStatus.status === 'completed' ? 'border-white/20 bg-white/5' : 
              stageStatus.status === 'in_progress' ? 'border-white/40 bg-white/10 scale-[1.02]' : 
              'border-white/5 opacity-40'
            }`}>
              <div className="flex items-center justify-between mb-3">
                {stageStatus.status === 'completed' ? (
                  <CheckCircle2 className="h-4 w-4 text-white" />
                ) : stageStatus.status === 'in_progress' ? (
                  <Loader2 className="h-4 w-4 text-white animate-spin" />
                ) : (
                  <Clock className="h-4 w-4 text-zinc-600" />
                )}
              </div>
              <p className="text-[10px] font-black uppercase tracking-widest text-zinc-400 mb-1">{stage.label}</p>
              <p className="text-[9px] text-zinc-600 uppercase font-bold">
                {stageStatus.status.replace('_', ' ')}
              </p>
            </div>
          );
        })}
      </div>

      <div className="flex flex-col md:flex-row justify-between items-center gap-6 pt-6 border-t border-white/5">
        <div className="flex items-center space-x-4">
          <div className="px-3 py-1 bg-white/5 rounded-md border border-white/10">
            <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-black flex items-center">
              <span className="mr-2">CURRENT OP:</span>
              <span className="text-white">{progress.progress?.current_step || 'Awaiting Logic'}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {progress.progress?.pr_url && (
            <a 
              href={progress.progress.pr_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 px-6 py-2 bg-white text-black rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-zinc-200 transition-all"
            >
              <span>Review PR</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
          {progress.status === 'completed' && (
            <div className="flex items-center space-x-2 px-6 py-2 bg-green-500/10 border border-green-500/30 text-green-400 rounded-full text-[10px] font-black uppercase tracking-widest">
              <ShieldCheck className="h-3 w-3" />
              <span>Fix Verified</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BugProgressTracker;
