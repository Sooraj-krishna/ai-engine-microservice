'use client';

import { AlertTriangle, Bug, FileText, ServerCrash } from 'lucide-react';

interface BugReportProps {
  issues: any[];
}

const getBugIcon = (type: string) => {
  switch (type) {
    case 'Deployment Configuration Error':
      return <ServerCrash className="h-5 w-5 text-cyan-400" />;
    case 'Broken or Missing Static Assets':
      return <FileText className="h-5 w-5 text-yellow-500" />;
    case 'Data Persistence and State Management Error':
      return <AlertTriangle className="h-5 w-5 text-blue-500" />;
    default:
      return <Bug className="h-5 w-5 text-gray-500" />;
  }
};

export function BugReport({ issues }: BugReportProps) {
  if (!issues || issues.length === 0) {
    return null;
  }

  const bugIssues = issues.filter(issue => issue.type === 'bug_report');

  if (bugIssues.length === 0) {
    return null;
  }

  return (
    <div className="bg-white border rounded-lg p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Bug Reports</h3>
      <div className="space-y-4">
        {bugIssues.map((issue, index) => (
          <div key={index} className="border-l-4 p-3 rounded-r-lg bg-gray-50 border-red-400">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                {getBugIcon(issue.data.type)}
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-900">{issue.data.type}</p>
                <p className="text-sm text-gray-700">{issue.description}</p>
                {issue.details && (
                  <p className="text-xs text-gray-500 mt-1">
                    <strong>Details:</strong> {issue.details}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
