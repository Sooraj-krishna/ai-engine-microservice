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
      {/* Configuration Form */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-bold text-zinc-300 mb-2 uppercase tracking-wider">
            Website URL
          </label>
          <input
            type="url"
            name="websiteUrl"
            value={formData.websiteUrl}
            onChange={handleInputChange}
            placeholder="https://your-website.com"
            className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 placeholder:text-zinc-600"
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-zinc-300 mb-2 uppercase tracking-wider">
            GitHub Repository
          </label>
          <input
            type="text"
            name="githubRepo"
            value={formData.githubRepo}
            onChange={handleInputChange}
            placeholder="username/repository-name"
            className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 placeholder:text-zinc-600"
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-zinc-300 mb-2 uppercase tracking-wider">
            Monitoring Mode
          </label>
          <select
            name="monitoringMode"
            value={formData.monitoringMode}
            onChange={handleInputChange}
            className="w-full px-3 py-2 bg-zinc-900 border border-zinc-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600"
          >
            <option value="simple">Simple Monitoring</option>
            <option value="ga_only">Google Analytics Only</option>
            <option value="ga_logs">GA + Logs</option>
          </select>
        </div>

        {/* Advanced Options Section */}
        <div className="border-t border-zinc-800 pt-4 mt-4">
          <h3 className="text-sm font-bold text-cyan-400 mb-3 uppercase tracking-wider">Advanced Options</h3>
          
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="useImprovedFixer"
                name="useImprovedFixer"
                checked={formData.useImprovedFixer}
                onChange={handleInputChange}
                className="h-4 w-4 text-red-600 focus:ring-red-500 border-zinc-700 rounded-lg bg-zinc-900"
              />
              <label htmlFor="useImprovedFixer" className="text-sm text-zinc-300">
                <span className="font-bold">Use Improved Fixer</span>
                <span className="block text-xs text-zinc-500 mt-1">
                  Enable advanced fixing with code diffs, chunking, and incremental fixes. 
                  More accurate but experimental.
                </span>
              </label>
            </div>
            
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="testFixesBeforeApply"
                name="testFixesBeforeApply"
                checked={formData.testFixesBeforeApply}
                onChange={handleInputChange}
                className="h-4 w-4 text-green-600 focus:ring-green-500 border-zinc-700 rounded-lg bg-zinc-900"
              />
              <label htmlFor="testFixesBeforeApply" className="text-sm text-zinc-300">
                <span className="font-bold">Test Fixes Before Applying</span>
                <span className="block text-xs text-zinc-500 mt-1">
                  Test fixes in isolated environment before creating PRs. Prevents bad fixes from going live.
                  <span className="text-green-400 font-semibold"> Recommended: ON</span>
                </span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons - All in one row */}
      <div className="flex gap-3 mt-6">
        <button
          onClick={testConnection}
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-white rounded-lg transition-all disabled:opacity-50"
        >
          <Settings className="h-4 w-4" />
          <span className="font-bold uppercase tracking-wider text-xs">Test Connection</span>
        </button>

        <button
          onClick={saveConfiguration}
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-700 hover:bg-green-600 border border-green-800 hover:border-green-700 text-white rounded-lg transition-all disabled:opacity-50"
        >
          <CheckCircle className="h-4 w-4" />
          <span className="font-bold uppercase tracking-wider text-xs">Save Config</span>
        </button>

        <button
          onClick={triggerMaintenance}
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-red-600 hover:to-red-500 text-white rounded-lg transition-all shadow-lg shadow-cyan-950/50 disabled:opacity-50"
        >
          <Play className="h-4 w-4" />
          <span className="font-bold uppercase tracking-wider text-xs">Run Maintenance</span>
        </button>
      </div>

      {/* Status Message */}
      {message && (
        <div className={`p-3 rounded-lg border ${
          status === 'success' ? 'bg-green-950/50 text-green-400 border-green-800/50' :
          status === 'error' ? 'bg-cyan-950/50 text-cyan-400 border-cyan-800/50' :
          'bg-blue-950/50 text-blue-400 border-blue-800/50'
        }`}>
          <div className="flex items-center space-x-2 font-mono text-sm">
            {status === 'success' && <CheckCircle className="h-4 w-4" />}
            {status === 'error' && <AlertCircle className="h-4 w-4" />}
            <span>{message}</span>
          </div>
        </div>
      )}
    </div>
  );
}
