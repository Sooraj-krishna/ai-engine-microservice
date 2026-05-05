'use client';

import { API_BASE_URL } from '@/lib/config';
import { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, XCircle, Clock, History, Cpu } from 'lucide-react';

interface Task {
  id: string;
  name: string;
  timestamp: string;
  status: string;
  ready: boolean;
}

export function TaskQueue() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTasks = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks`);
      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks || []);
      }
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 3000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SUCCESS': return <CheckCircle2 className="h-3 w-3 text-white" />;
      case 'FAILURE': return <XCircle className="h-3 w-3 text-white" />;
      case 'STARTED':
      case 'PROGRESS': return <Loader2 className="h-3 w-3 animate-spin text-white" />;
      default: return <Clock className="h-3 w-3 text-zinc-700" />;
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-zinc-800">
        <Loader2 className="h-5 w-5 animate-spin mb-3" />
        <span className="text-[10px] font-black uppercase tracking-[0.3em]">Querying Tasks...</span>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {tasks.length === 0 ? (
        <div className="py-12 text-center border border-white/5 rounded-2xl bg-white/[0.01]">
          <Cpu className="h-6 w-6 mx-auto mb-4 text-zinc-800" />
          <p className="text-[9px] font-black uppercase tracking-[0.3em] text-zinc-700">No background modules active</p>
        </div>
      ) : (
        tasks.map((task) => (
          <div 
            key={task.id} 
            className="group flex items-center justify-between p-4 rounded-xl hover:bg-white/[0.03] transition-all border border-transparent hover:border-white/5"
          >
            <div className="flex items-center gap-4 min-0">
              <div className="shrink-0">
                {getStatusIcon(task.status)}
              </div>
              <div className="min-w-0">
                <h3 className="text-[11px] font-bold text-zinc-400 group-hover:text-white transition-colors truncate uppercase tracking-tight">
                  {task.name}
                </h3>
                <p className="text-[8px] text-zinc-700 font-mono truncate">ID: {task.id.slice(0, 12)}</p>
              </div>
            </div>

            <div className="flex flex-col items-end gap-1 ml-4 shrink-0">
              <span className={`text-[8px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full border ${
                task.status === 'SUCCESS' ? 'border-white/20 text-white' :
                task.status === 'FAILURE' ? 'border-white/5 text-zinc-700' :
                'border-white/10 text-zinc-400 animate-pulse'
              }`}>
                {task.status}
              </span>
              <span className="text-[8px] text-zinc-800 font-bold tabular-nums">
                {new Date(task.timestamp).toLocaleTimeString([], { hour12: false })}
              </span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
