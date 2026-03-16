'use client';

import { useState, useEffect } from 'react';
import { Play, Settings, CheckCircle, AlertCircle } from 'lucide-react';

interface ConfigurationFormProps {
  onConfigured: (configured: boolean) => void;
  onStatusUpdate: (status: any) => void;
}

export function ConfigurationForm({ onConfigured, onStatusUpdate }: ConfigurationFormProps) {
  const [formData, setFormData] = useState({
    websiteUrl: '',
    githubRepo: '',
    monitoringMode: 'simple',
    useImprovedFixer: false,
    testFixesBeforeApply: true
  });

  // Load current configuration on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await fetch('http://localhost:8000/config');
        if (response.ok) {
          const config = await response.json();
          setFormData(prev => ({
            ...prev,
            websiteUrl: config.website_url || '',
            githubRepo: config.github_repo || '',
            monitoringMode: config.monitoring_mode || 'simple',
            useImprovedFixer: config.use_improved_fixer || false,
            testFixesBeforeApply: config.test_fixes_before_apply !== undefined ? config.test_fixes_before_apply : true
          }));
        }
      } catch (error) {
        console.error('Failed to load config:', error);
      }
    };
    loadConfig();
  }, []);

  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData(prev => ({ 
      ...prev, 
      [name]: type === 'checkbox' ? checked : value 
    }));
  };

  const testConnection = async () => {
    setIsLoading(true);
    setStatus('testing');
    setMessage('Testing connection to AI Engine...');

    try {
      // Test connection to the AI Engine
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setStatus('success');
        setMessage('✅ Successfully connected to AI Engine!');
        onConfigured(true);
      } else {
        throw new Error('Failed to connect to AI Engine');
      }
    } catch (error) {
      setStatus('error');
      setMessage('❌ Failed to connect to AI Engine. Make sure it\'s running on port 8000.');
      onConfigured(false);
    } finally {
      setIsLoading(false);
    }
  };

  const saveConfiguration = async () => {
    setIsLoading(true);
    setStatus('testing');
    setMessage('Saving configuration...');

    try {
      // Save configuration to the AI Engine
      const response = await fetch('http://localhost:8000/configure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          websiteUrl: formData.websiteUrl,
          githubRepo: formData.githubRepo,
          monitoringMode: formData.monitoringMode,
          useImprovedFixer: formData.useImprovedFixer,
          testFixesBeforeApply: formData.testFixesBeforeApply,
        }),
      });

      if (response.ok) {
        setStatus('success');
        setMessage('✅ Configuration saved successfully!');
        onConfigured(true);
      } else {
        throw new Error('Failed to save configuration');
      }
    } catch (error) {
      setStatus('error');
      setMessage('❌ Failed to save configuration. Check your inputs.');
      onConfigured(false);
    } finally {
      setIsLoading(false);
    }
  };

  const triggerMaintenance = async () => {
    setIsLoading(true);
    setStatus('testing');
    setMessage('Starting maintenance cycle...');
    

    try {
      const response = await fetch('http://localhost:8000/run', {
        method: 'POST',
      });

      if (response.ok) {
        setStatus('success');
        setMessage('✅ Maintenance cycle started! Check logs for progress.');
      } else {
        throw new Error('Failed to start maintenance cycle');
      }
    } catch (error) {
      setStatus('error');
      setMessage('❌ Failed to start maintenance cycle.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* GitHub Repository */}
      <div>
        <label className="block text-sm font-medium text-white/60 mb-2">
          GITHUB REPOSITORY
        </label>
        <div className="relative">
          <input
            type="text"
            name="githubRepo"
            value={formData.githubRepo}
            onChange={handleInputChange}
            placeholder="username/repo"
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors"
          />
          <div className="absolute right-3 top-3 text-white/20">
            <svg viewBox="0 0 24 24" className="w-6 h-6 fill-current">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Monitoring Mode */}
      <div>
        <label className="block text-sm font-medium text-white/60 mb-2">
          MONITORING MODE
        </label>
        <div className="relative">
          <select
            name="monitoringMode"
            value={formData.monitoringMode}
            onChange={handleInputChange}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white appearance-none focus:outline-none focus:border-white/30 transition-colors"
          >
            <option value="standard" className="bg-black text-white">Standard (Issues & PRs)</option>
            <option value="deep" className="bg-black text-white">Deep (Code Analysis)</option>
            <option value="realtime" className="bg-black text-white">Real-time (Active Monitoring)</option>
          </select>
          <div className="absolute right-4 top-3.5 text-white/40 pointer-events-none">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4 pt-2">
        <button
          onClick={testConnection}
          disabled={isLoading}
          className="flex-1 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white font-bold uppercase tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isLoading && status === 'testing' ? (
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/20 border-t-white"></div>
          ) : (
            <Settings className="h-4 w-4" />
          )}
          <span>Test Connection</span>
        </button>
        
        <button
          onClick={saveConfiguration}
          disabled={isLoading}
          className="flex-1 px-6 py-3 bg-white text-black hover:bg-gray-100 rounded-lg font-bold uppercase tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg flex items-center justify-center gap-2"
        >
          <CheckCircle className="h-4 w-4" />
          <span>Save Config</span>
        </button>
      </div>

      {/* Connection Status Message */}
      {message && (
        <div className={`mt-4 p-4 rounded-lg flex items-start gap-3 ${
          status === 'success' 
            ? 'bg-green-500/10 border border-green-500/20 text-green-400' 
            : 'bg-red-500/10 border border-red-500/20 text-red-400'
        }`}>
          {status === 'success' ? (
            <CheckCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          )}
          <p className="text-sm">{message}</p>
        </div>
      )}

      {/* Maintenance Trigger */}
      <div className="pt-6 mt-6 border-t border-white/10">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-bold uppercase tracking-wide">Manual Maintenance</h3>
            <p className="text-sm text-white/40 mt-1">Trigger immediate codebase scan</p>
          </div>
          <button
            onClick={triggerMaintenance}
            className="px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/10 rounded-lg text-white font-bold uppercase tracking-wider transition-all flex items-center gap-2"
          >
            <Play className="h-4 w-4" />
            <span>Run Now</span>
          </button>
        </div>
      </div>
    </div>
  );
}
