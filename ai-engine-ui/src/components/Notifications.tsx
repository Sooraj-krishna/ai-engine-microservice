'use client';

import { API_BASE_URL } from '@/lib/config';
import React, { useEffect, useState } from 'react';
import { 
  Bell, 
  CheckCircle, 
  AlertTriangle, 
  AlertOctagon, 
  Info, 
  Clock, 
  RefreshCw,
  Trash2,
  X,
  ChevronRight
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

  const fetchNotifications = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/notifications?limit=15`);
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearItem = async (timestamp: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/notifications/item?timestamp=${encodeURIComponent(timestamp)}`, { method: 'DELETE' });
      if (response.ok) {
        setNotifications(prev => prev.filter(n => n.timestamp !== timestamp));
      }
    } catch (error) {
      console.error('Failed to clear notification:', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'success': return <CheckCircle className="h-3 w-3 text-white" />;
      case 'warning': return <AlertTriangle className="h-3 w-3 text-white" />;
      case 'critical':
      case 'high': return <AlertOctagon className="h-3 w-3 text-white" />;
      default: return <Info className="h-3 w-3 text-white" />;
    }
  };

  if (isLoading && notifications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-zinc-800">
        <RefreshCw className="h-5 w-5 animate-spin mb-3" />
        <span className="text-[10px] font-black uppercase tracking-[0.3em]">Syncing Alerts...</span>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {notifications.length === 0 ? (
        <div className="py-12 text-center border border-white/5 rounded-2xl bg-white/[0.01]">
          <Bell className="h-6 w-6 mx-auto mb-4 text-zinc-800" />
          <p className="text-[9px] font-black uppercase tracking-[0.3em] text-zinc-700">No active alerts recorded</p>
        </div>
      ) : (
        notifications.map((notif, idx) => (
          <div 
            key={idx} 
            className="group relative flex items-start gap-4 p-4 rounded-xl hover:bg-white/[0.03] transition-all border border-transparent hover:border-white/5"
          >
            <div className="mt-1 relative shrink-0">
              {getSeverityIcon(notif.severity)}
              {notif.severity === 'critical' && (
                <div className="absolute -top-1 -right-1 w-1 h-1 bg-white rounded-full animate-pulse shadow-[0_0_8px_white]" />
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[9px] font-black uppercase tracking-widest text-zinc-500 group-hover:text-white transition-colors">
                  System Notification · {notif.type.replace(/_/g, ' ')}
                </span>
                <span className="text-[8px] font-bold text-zinc-700 tabular-nums">
                  {new Date(notif.timestamp).toLocaleTimeString([], { hour12: false })}
                </span>
              </div>
              <p className="text-[11px] text-zinc-500 leading-relaxed font-light group-hover:text-zinc-300 transition-colors">
                {notif.message}
              </p>
            </div>

            <button 
              onClick={() => clearItem(notif.timestamp)}
              className="opacity-0 group-hover:opacity-100 p-1 hover:text-white text-zinc-700 transition-all"
            >
              <X className="h-3 w-3" />
            </button>
          </div>
        ))
      )}
    </div>
  );
}
