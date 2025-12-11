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
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Website URL
          </label>
          <input
            type="url"
            name="websiteUrl"
            value={formData.websiteUrl}
            onChange={handleInputChange}
            placeholder="https://your-website.com"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            GitHub Repository
          </label>
          <input
            type="text"
            name="githubRepo"
            value={formData.githubRepo}
            onChange={handleInputChange}
            placeholder="username/repository-name"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monitoring Mode
          </label>
          <select
            name="monitoringMode"
            value={formData.monitoringMode}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="simple">Simple Monitoring</option>
            <option value="ga_only">Google Analytics Only</option>
            <option value="ga_logs">GA + Logs</option>
          </select>
        </div>

        {/* Advanced Options Section */}
        <div className="border-t pt-4 mt-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Advanced Options</h3>
          
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="useImprovedFixer"
                name="useImprovedFixer"
                checked={formData.useImprovedFixer}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="useImprovedFixer" className="text-sm text-gray-700">
                <span className="font-medium">Use Improved Fixer</span>
                <span className="block text-xs text-gray-500 mt-1">
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
                className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
              <label htmlFor="testFixesBeforeApply" className="text-sm text-gray-700">
                <span className="font-medium">Test Fixes Before Applying</span>
                <span className="block text-xs text-gray-500 mt-1">
                  Test fixes in isolated environment before creating PRs. Prevents bad fixes from going live.
                  <span className="text-green-600 font-semibold"> Recommended: ON</span>
                </span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-3">
        <button
          onClick={testConnection}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          <Settings className="h-4 w-4" />
          <span>Test Connection</span>
        </button>

        <button
          onClick={saveConfiguration}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          <CheckCircle className="h-4 w-4" />
          <span>Save Config</span>
        </button>

        <button
          onClick={triggerMaintenance}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
        >
          <Play className="h-4 w-4" />
          <span>Run Maintenance</span>
        </button>
      </div>

      {/* Status Message */}
      {message && (
        <div className={`p-3 rounded-md ${
          status === 'success' ? 'bg-green-50 text-green-800' :
          status === 'error' ? 'bg-red-50 text-red-800' :
          'bg-blue-50 text-blue-800'
        }`}>
          <div className="flex items-center space-x-2">
            {status === 'success' && <CheckCircle className="h-4 w-4" />}
            {status === 'error' && <AlertCircle className="h-4 w-4" />}
            <span>{message}</span>
          </div>
        </div>
      )}
    </div>
  );
}
