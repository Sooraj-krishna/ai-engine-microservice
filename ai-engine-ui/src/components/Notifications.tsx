'use client';

import React, { useEffect, useState } from 'react';
import { 
  Bell, 
  CheckCircle, 
  AlertTriangle, 
  AlertOctagon, 
  Info, 
  ExternalLink,
  Clock,
  RefreshCw,
  Trash2,
  X
} from 'lucide-react';

interface Notification {
  type: string;
  severity: string;
  message: string;
  timestamp: string;
  data: any;
}

export function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchNotifications = async () => {
    try {
      const response = await fetch('http://localhost:8000/notifications?limit=20');
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setLastUpdated(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearAll = async () => {
    if (!confirm('Are you sure you want to clear all notifications?')) return;
    
    // Optimistic update
    const previousNotifications = [...notifications];
    setNotifications([]);
    
    try {
      const response = await fetch('http://localhost:8000/notifications', { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to clear notifications');
      }
    } catch (error) {
      console.error('Failed to clear notifications:', error);
      // Revert if failed
      setNotifications(previousNotifications);
      alert('Failed to clear notifications. Please try again.');
    }
  };

  const clearItem = async (timestamp: string) => {
    try {
      const response = await fetch(`http://localhost:8000/notifications/item?timestamp=${encodeURIComponent(timestamp)}`, { method: 'DELETE' });
      if (response.ok) {
        setNotifications(prev => prev.filter(n => n.timestamp !== timestamp));
      }
    } catch (error) {
      console.error('Failed to clear notification:', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const getIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'success': return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'warning': return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
      case 'critical':
      case 'high': return <AlertOctagon className="h-5 w-5 text-red-500" />;
      default: return <Info className="h-5 w-5 text-blue-400" />;
    }
  };

  const getSeverityStyle = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'success': return 'border-green-900/30 bg-green-950/10';
      case 'warning': return 'border-yellow-900/30 bg-yellow-950/10';
      case 'critical':
      case 'high': return 'border-red-900/30 bg-red-950/20';
      default: return 'border-blue-900/30 bg-blue-950/10';
    }
  };

  if (isLoading && notifications.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 text-cyan-400 animate-spin mr-3" />
        <span className="text-zinc-500 font-mono uppercase tracking-widest text-sm">Synchronizing alerts...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Bell className="h-5 w-5 text-red-gradient" />
          <h3 className="text-lg font-bold text-white uppercase tracking-wider">System Alerts</h3>
        </div>
        <div className="flex items-center space-x-4">
          <button 
            onClick={clearAll}
            className="flex items-center text-[10px] text-zinc-500 hover:text-red-400 uppercase tracking-tighter transition-colors group"
            title="Clear All"
          >
            <Trash2 className="h-3 w-3 mr-1 group-hover:animate-pulse" />
            Clear All
          </button>
          <div className="flex items-center text-[10px] text-zinc-500 uppercase tracking-tighter border-l border-zinc-800 pl-4">
            <Clock className="h-3 w-3 mr-1" />
            Last update: {lastUpdated.toLocaleTimeString()}
          </div>
        </div>
      </div>

      <div className="max-h-[400px] overflow-y-auto pr-2 custom-scrollbar space-y-3">
        {notifications.length === 0 ? (
          <div className="text-center py-12 border border-zinc-800 rounded-lg bg-zinc-900/20">
            <Info className="h-8 w-8 mx-auto mb-2 text-zinc-700" />
            <p className="text-zinc-500 text-sm uppercase tracking-widest">No recent notifications</p>
          </div>
        ) : (
          notifications.map((notif, idx) => (
            <div 
              key={idx} 
              className={`p-4 rounded-lg border flex items-start space-x-4 transition-all hover:border-zinc-700 relative group/item ${getSeverityStyle(notif.severity)}`}
            >
              <button 
                onClick={() => clearItem(notif.timestamp)}
                className="absolute top-2 right-2 p-1 text-zinc-600 hover:text-white opacity-0 group-hover/item:opacity-100 transition-opacity"
                title="Dismiss"
              >
                <X className="h-3 w-3" />
              </button>
              <div className="mt-1 flex-shrink-0">
                {getIcon(notif.severity)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start mb-1">
                  <span className={`text-[10px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded border ${
                    notif.severity === 'success' ? 'text-green-400 border-green-900/50' :
                    notif.severity === 'warning' ? 'text-yellow-400 border-yellow-900/50' :
                    notif.severity === 'critical' || notif.severity === 'high' ? 'text-red-400 border-red-900/50' :
                    'text-blue-400 border-blue-900/50'
                  }`}>
                    {notif.type.replace('_', ' ')}
                  </span>
                  <span className="text-[10px] text-zinc-500 font-mono">
                    {new Date(notif.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-zinc-300 text-sm leading-relaxed mb-2">
                  {notif.message}
                </p>
                
                {notif.data?.pr_url && (
                  <a 
                    href={notif.data.pr_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-xs text-cyan-400 hover:text-cyan-300 transition-colors uppercase font-bold tracking-tighter"
                  >
                    View Pull Request <ExternalLink className="h-3 w-3 ml-1" />
                  </a>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
