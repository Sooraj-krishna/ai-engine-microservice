'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle2, XCircle, Clock, History } from 'lucide-react';

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
      const response = await fetch('http://localhost:8000/tasks');
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
    const interval = setInterval(fetchTasks, 3000); // Update every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
      case 'FAILURE':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'STARTED':
      case 'PROGRESS':
        return <Loader2 className="h-4 w-4 text-cyan-500 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-zinc-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <Badge className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20">Success</Badge>;
      case 'FAILURE':
        return <Badge className="bg-red-500/10 text-red-500 border-red-500/20">Failed</Badge>;
      case 'STARTED':
      case 'PROGRESS':
        return <Badge className="bg-cyan-500/10 text-cyan-500 border-cyan-500/20">Running</Badge>;
      case 'PENDING':
        return <Badge className="bg-amber-500/10 text-amber-500 border-amber-500/20">Pending</Badge>;
      default:
        return <Badge variant="outline" className="text-zinc-500 border-zinc-500/20">{status}</Badge>;
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 text-cyan-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.length === 0 ? (
        <div className="text-center p-8 border border-dashed border-zinc-800 rounded-lg">
          <History className="h-8 w-8 text-zinc-600 mx-auto mb-2" />
          <p className="text-zinc-500 text-sm">No recent background tasks</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
          {tasks.map((task) => (
            <div 
              key={task.id} 
              className="flex items-center justify-between p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 hover:border-zinc-700 transition-colors"
            >
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="shrink-0">{getStatusIcon(task.status)}</div>
                <div className="min-w-0">
                  <h3 className="text-sm font-medium text-zinc-200 truncate">{task.name}</h3>
                  <p className="text-[10px] text-zinc-500 font-mono truncate">{task.id}</p>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1 shrink-0 ml-4">
                {getStatusBadge(task.status)}
                <span className="text-[10px] text-zinc-600">
                  {new Date(task.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
