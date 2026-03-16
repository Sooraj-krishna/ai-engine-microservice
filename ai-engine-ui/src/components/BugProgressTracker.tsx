import React, { useState, useEffect } from 'react';
import './BugProgressTracker.css';

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
  refreshInterval?: number;  // milliseconds
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
      const response = await fetch(`http://localhost:8000/bugs/${bugId}/progress`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch progress');
      }
      
      const data = await response.json();
      setProgress(data);
      setError(null);
      setLoading(false);
    } catch (err) {
      setError('Failed to load progress');
      setLoading(false);
    }
  };

  const getStageIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✓';
      case 'in_progress': return '⏳';
      default: return '⭘';
    }
  };

  const getStageColor = (status: string) => {
    switch (status) {
      case 'completed': return '#10b981';
      case 'in_progress': return '#3b82f6';
      default: return '#9ca3af';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#ef4444';
      case 'high': return '#f97316';
      case 'medium': return '#eab308';
      default: return '#22c55e';
    }
  };

  if (loading) {
    return <div className="progress-tracker loading">Loading progress...</div>;
  }

  if (error || !progress) {
    return <div className="progress-tracker error">{error || 'Progress not found'}</div>;
  }

  // Defensive check: Ensure progress structure exists
  if (!progress.progress || !progress.progress.stages) {
    return (
      <div className="progress-tracker error">
        <p>⚠️ Progress data not available for this bug</p>
        <p className="error-hint">This bug may have been created before progress tracking was implemented.</p>
      </div>
    );
  }

  const stages = [
    { key: 'plan_generation', label: 'Plan Generation' },
    { key: 'validation', label: 'Validation' },
    { key: 'execution', label: 'Execution' },
    { key: 'git_push', label: 'Git Push' }
  ];

  return (
    <div className="progress-tracker">
      <div className="tracker-header">
        <div className="tracker-title">
          <span 
            className="severity-badge-small"
            style={{ backgroundColor: getSeverityColor(progress.severity) }}
          >
            {progress.severity.toUpperCase()}
          </span>
          <h3>Fixing: {progress.bug.type?.replace(/_/g, ' ') || 'Unknown Bug'}</h3>
        </div>
        <div className="tracker-percentage">{progress.progress?.percentage || 0}%</div>
      </div>

      <div className="progress-bar-container">
        <div 
          className="progress-bar-fill" 
          style={{ 
            width: `${progress.progress?.percentage || 0}%`,
            transition: 'width 0.5s ease'
          }}
        />
      </div>

      <div className="stages-list">
        {stages.map(stage => {
          const stageStatus = progress.progress?.stages?.[stage.key as keyof typeof progress.progress.stages] || 
                              { status: 'pending' as const, started_at: null, completed_at: null };
          return (
            <div 
              key={stage.key}
              className={`stage-item ${stageStatus.status}`}
              style={{ borderLeftColor: getStageColor(stageStatus.status) }}
            >
              <span 
                className="stage-icon"
                style={{ color: getStageColor(stageStatus.status) }}
              >
                {getStageIcon(stageStatus.status)}
              </span>
              <span className="stage-label">{stage.label}</span>
              {stageStatus.completed_at && (
                <span className="stage-time">
                  {new Date(stageStatus.completed_at).toLocaleTimeString()}
                </span>
              )}
            </div>
          );
        })}
      </div>

      <div className="current-step">
        <strong>Current:</strong> {progress.progress?.current_step || 'Waiting...'}
      </div>

      {progress.progress?.pr_url && (
        <div className="pr-link">
          <a 
            href={progress.progress.pr_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-pr"
          >
            🔗 View Pull Request
          </a>
        </div>
      )}

      {progress.status === 'completed' && (
        <div className="completion-badge">
          ✅ Completed successfully!
        </div>
      )}
    </div>
  );
};

export default BugProgressTracker;
