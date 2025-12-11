'use client';

import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react';

type Severity = 'high' | 'medium' | 'low';

interface LogReportProps {
  logs: string[];
}

const severityMap = (line: string): Severity => {
  const upper = line.toUpperCase();
  if (upper.includes('[ERROR]') || upper.includes('FAIL')) return 'high';
  if (upper.includes('[WARNING]') || upper.includes('[WARN]')) return 'medium';
  return 'low';
};

const friendlyMessage = (line: string) => {
  const clean = line.replace(/^\[.*?\]\s*/i, '').trim();
  if (/websocket connection established/i.test(line)) return 'Live updates connected.';
  if (/websocket connection closed/i.test(line)) return 'Live updates disconnected.';
  if (/maintenance cycle started/i.test(line)) return 'Maintenance run started.';
  if (/pull request created/i.test(line)) return 'A fix was proposed for review.';
  if (/health check.*failed/i.test(line)) return 'Health check failed; please review.';
  if (/testing fixes.*failed/i.test(line)) return 'Some fixes failed tests and were skipped.';
  if (/generated and validated/i.test(line)) return 'Safe fixes generated and validated.';
  return clean || 'System message';
};

const severityLabel = {
  high: 'High (needs attention)',
  medium: 'Medium (check soon)',
  low: 'Low (informational)',
};

const severityIcon = {
  high: <XCircle className="h-4 w-4 text-red-600" />,
  medium: <AlertTriangle className="h-4 w-4 text-yellow-600" />,
  low: <Info className="h-4 w-4 text-blue-600" />,
};

export function LogReport({ logs }: LogReportProps) {
  const summaries = { high: [] as string[], medium: [] as string[], low: [] as string[] };

  logs.slice(-200).forEach((line) => {
    const sev = severityMap(line);
    summaries[sev].push(line);
  });

  const counts = {
    high: summaries.high.length,
    medium: summaries.medium.length,
    low: summaries.low.length,
  };

  const recent = (sev: Severity) =>
    summaries[sev]
      .slice(-3)
      .reverse()
      .map((l, idx) => (
        <li key={`${sev}-${idx}`} className="text-sm text-gray-700">
          {friendlyMessage(l)}
        </li>
      ));

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <h3 className="text-lg font-semibold text-gray-800">Simple Report</h3>
        </div>
        <div className="text-sm text-gray-500">Based on recent activity</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {(['high', 'medium', 'low'] as Severity[]).map((sev) => (
          <div key={sev} className="border rounded-md p-3">
            <div className="flex items-center space-x-2 mb-2">
              {severityIcon[sev]}
              <span className="text-sm font-medium text-gray-800">{severityLabel[sev]}</span>
              <span
                className={`text-xs px-2 py-1 rounded-full ${
                  sev === 'high'
                    ? 'bg-red-100 text-red-700'
                    : sev === 'medium'
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-blue-100 text-blue-700'
                }`}
              >
                {counts[sev]}
              </span>
            </div>
            <ul className="space-y-1">
              {counts[sev] === 0 ? (
                <li className="text-xs text-gray-500">No messages</li>
              ) : (
                recent(sev)
              )}
            </ul>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-gray-500">
        Tips: High = immediate attention (errors), Medium = warnings, Low = informational updates.
      </div>
    </div>
  );
}

