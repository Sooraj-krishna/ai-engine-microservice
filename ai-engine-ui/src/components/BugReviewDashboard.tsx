import React, { useState, useEffect } from 'react';
import './BugReviewDashboard.css';
import BugProgressTracker from './BugProgressTracker';

interface Bug {
  id: string;
  type: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  target_file: string;
  detected_at: string;
  framework: string;
  language: string;
}

interface BugsBySerity {
  critical: Bug[];
  high: Bug[];
  medium: Bug[];
  low: Bug[];
}

interface InProgressBug {
  bug_id: string;
  severity: string;
  status: string;
  bug: {
    type: string;
    description: string;
  };
  processing_started_at: string;
}

const BugReviewDashboard: React.FC = () => {
  const [bugs, setBugs] = useState<BugsBySerity>({
    critical: [],
    high: [],
    medium: [],
    low: []
  });
  const [summary, setSummary] = useState({ critical: 0, high: 0, medium: 0, low: 0 });
  const [activeTab, setActiveTab] = useState<'critical' | 'high' | 'medium' | 'low' | 'in_progress'>('critical');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState<string | null>(null);
  const [inProgressBugs, setInProgressBugs] = useState<InProgressBug[]>([]);

  useEffect(() => {
    fetchPendingBugs();
    fetchInProgressBugs();
    
    // Refresh in-progress bugs every 3 seconds
    const interval = setInterval(fetchInProgressBugs, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchPendingBugs = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/bugs/pending');
      const data = await response.json();
      
      setBugs(data.bugs_by_severity);
      setSummary(data.summary);
      setError(null);
    } catch (err) {
      setError('Failed to load bugs. Make sure the server is running.');
      console.error('Error fetching bugs:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchInProgressBugs = async () => {
    try {
      const response = await fetch('http://localhost:8000/bugs/in-progress');
      const data = await response.json();
      setInProgressBugs(data.bugs || []);
    } catch (err) {
      console.error('Error fetching in-progress bugs:', err);
    }
  };

  const approveBug = async (bugId: string) => {
    try {
      setApproving(bugId);
      const response = await fetch(`http://localhost:8000/bugs/${bugId}/approve`, {
        method: 'POST'
      });
      
      if (response.ok) {
        // Remove approved bug from the list
        if (activeTab !== 'in_progress') {
          setBugs(prev => ({
            ...prev,
            [activeTab]: prev[activeTab].filter(bug => bug.id !== bugId)
          }));
          setSummary(prev => ({
            ...prev,
            [activeTab]: prev[activeTab] - 1
          }));
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`Failed to approve bug: ${errorData.error || response.statusText}`);
      }
    } catch (err) {
      alert('Error approving bug: Connection failed');
      console.error(err);
    } finally {
      setApproving(null);
    }
  };

  const approveBySeverity = async (severity: string) => {
    if (!confirm(`Approve all ${summary[severity as keyof typeof summary]} ${severity} severity bugs?`)) {
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/bugs/approve-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ severities: [severity] })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Approved ${data.approved} bugs`);
        fetchPendingBugs(); // Refresh
      }
    } catch (err) {
      alert('Error approving bugs');
      console.error(err);
    }
  };

  const clearFailedBugs = async () => {
    if (!confirm('Clear all failed bugs from the queue?')) {
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/bugs/failed', {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(data.message);
        fetchPendingBugs();
      }
    } catch (err) {
      alert('Error clearing failed bugs');
      console.error(err);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#ef4444';
      case 'high': return '#f97316';
      case 'medium': return '#eab308';
      case 'low': return '#22c55e';
      default: return '#6b7280';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="bug-review-dashboard">
        <div className="loading">Loading bugs...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bug-review-dashboard">
        <div className="error-message">
          <h3>⚠️ {error}</h3>
          <button onClick={fetchPendingBugs}>Retry</button>
        </div>
      </div>
    );
  }

  const totalBugs = summary.critical + summary.high + summary.medium + summary.low;

  return (
    <div className="bug-review-dashboard">
      <div className="dashboard-header">
        <h1>🐛 Bug Review Dashboard</h1>
        <p className="subtitle">
          {totalBugs} bugs detected and waiting for your approval
        </p>
        <div className="header-actions">
          <button onClick={fetchPendingBugs} className="btn-refresh">
            🔄 Refresh
          </button>
          <button onClick={clearFailedBugs} className="btn-clear">
            🗑️ Clear Failed
          </button>
        </div>
      </div>

      <div className="severity-tabs">
        {(['critical', 'high', 'medium', 'low'] as const).map(severity => (
          <button
            key={severity}
            className={`tab ${activeTab === severity ? 'active' : ''}`}
            onClick={() => setActiveTab(severity)}
            style={{
              borderBottom: activeTab === severity 
                ? `3px solid ${getSeverityColor(severity)}` 
                : 'none'
            }}
          >
            <span className="tab-icon">{getSeverityIcon(severity)}</span>
            <span className="tab-label">
              {severity.charAt(0).toUpperCase() + severity.slice(1)}
            </span>
            <span className="tab-count">{summary[severity]}</span>
          </button>
        ))}
        <button
          className={`tab ${activeTab === 'in_progress' ? 'active' : ''}`}
          onClick={() => setActiveTab('in_progress')}
          style={{
            borderBottom: activeTab === 'in_progress' 
              ? `3px solid #3b82f6` 
              : 'none'
          }}
        >
          <span className="tab-icon">⚡</span>
          <span className="tab-label">In Progress</span>
          <span className="tab-count">{inProgressBugs.length}</span>
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'in_progress' ? (
          <>
            <div className="tab-panel-header">
              <h2>⚡ Bugs Being Processed ({inProgressBugs.length})</h2>
              <button 
                onClick={() => {
                  fetchPendingBugs();
                  fetchInProgressBugs();
                }}
                className="btn-refresh-small"
              >
                🔄 Refresh
              </button>
            </div>

            {inProgressBugs.length === 0 ? (
              <div className="empty-state">
                <p>✅ No bugs currently being processed</p>
              </div>
            ) : (
              <div className="progress-list">
                {inProgressBugs.map((bug) => (
                  <BugProgressTracker 
                    key={bug.bug_id} 
                    bugId={bug.bug_id}
                    refreshInterval={2000}
                  />
                ))}
              </div>
            )}
          </>
        ) : (
          <>
            <div className="tab-panel-header">
              <h2>
                {getSeverityIcon(activeTab)} {activeTab.toUpperCase()} Severity Bugs 
                ({summary[activeTab as keyof typeof summary]})
              </h2>
              {summary[activeTab as keyof typeof summary] > 0 && (
                <button 
                  onClick={() => approveBySeverity(activeTab)}
                  className="btn-approve-all"
                  style={{ backgroundColor: getSeverityColor(activeTab) }}
                >
                  ✓ Approve All {activeTab}
                </button>
              )}
            </div>

            {bugs[activeTab as keyof BugsBySerity].length === 0 ? (
              <div className="empty-state">
                <p>✅ No {activeTab} severity bugs pending approval</p>
              </div>
            ) : (
              <div className="bug-list">
                {bugs[activeTab as keyof BugsBySerity].map((bug) => (
                  <div key={bug.id} className="bug-card">
                    <div className="bug-card-header">
                      <span 
                        className="severity-badge"
                        style={{ backgroundColor: getSeverityColor(bug.severity) }}
                      >
                        {getSeverityIcon(bug.severity)} {bug.severity.toUpperCase()}
                      </span>
                      <span className="bug-type">{bug.type.replace(/_/g, ' ')}</span>
                    </div>

                    <div className="bug-description">
                      <p>{bug.description}</p>
                    </div>

                    <div className="bug-details">
                      <div className="detail-item">
                        <strong>Target:</strong> {bug.target_file || 'N/A'}
                      </div>
                      <div className="detail-item">
                        <strong>Stack:</strong> {bug.framework} + {bug.language}
                      </div>
                      <div className="detail-item">
                        <strong>Detected:</strong> {new Date(bug.detected_at).toLocaleString()}
                      </div>
                    </div>

                    <div className="bug-actions">
                      <button
                        onClick={() => approveBug(bug.id)}
                        disabled={approving === bug.id}
                        className="btn-approve"
                      >
                        {approving === bug.id ? '⏳ Approving...' : '✓ Approve & Fix'}
                      </button>
                      <button className="btn-ignore">
                        ✕ Ignore
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default BugReviewDashboard;
