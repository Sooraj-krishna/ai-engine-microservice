"use client";

import React, { useState } from 'react';
import { Check, X, Edit2, Code2, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from './ui/button';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    message_type?: string;
    intent?: string;
    has_plan?: boolean;
    change_id?: string;
    requires_approval?: boolean;
    plan?: any;
    [key: string]: any;
  };
}

interface ChatMessageProps {
  message: Message;
  onApply?: (changeId: string) => Promise<any>;
  onReject?: (changeId: string, reason?: string) => Promise<any>;
  onRefine?: (refinementMessage: string) => Promise<any>;
}

export function ChatMessage({ message, onApply, onReject, onRefine }: ChatMessageProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [refineInput, setRefineInput] = useState('');
  const [showRefineInput, setShowRefineInput] = useState(false);

  const isUser = message.role === 'user';
  const hasPlan = message.metadata?.has_plan;
  const plan = message.metadata?.plan;
  const changeId = message.metadata?.change_id;
  const requiresApproval = message.metadata?.requires_approval;

  const handleApply = async () => {
    if (changeId && onApply) {
      await onApply(changeId);
    }
  };

  const handleReject = async () => {
    if (changeId && onReject) {
      await onReject(changeId);
    }
  };

  const handleRefine = async () => {
    if (refineInput.trim() && onRefine) {
      await onRefine(refineInput);
      setRefineInput('');
      setShowRefineInput(false);
    }
  };

  // Format message content (handle markdown-style formatting)
  const formatContent = (content: string) => {
    return content.split('\n').map((line, i) => {
      // Bold text
      line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // Check if it's a heading
      if (line.startsWith('**') && line.endsWith('**')) {
        return <div key={i} className="font-semibold mt-2 mb-1" dangerouslySetInnerHTML={{ __html: line }} />;
      }
      
      // Regular line
      return line ? (
        <p key={i} className="mb-0.5" dangerouslySetInnerHTML={{ __html: line }} />
      ) : (
        <br key={i} />
      );
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message bubble */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
              : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
          }`}
        >
          <div className="text-sm whitespace-pre-wrap">{formatContent(message.content)}</div>
        </div>

        {/* Plan details (if applicable) */}
        {hasPlan && plan && !isUser && (
          <div className="mt-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl overflow-hidden">
            {/* Plan header */}
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="w-full px-4 py-2 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-600 transition"
            >
              <div className="flex items-center gap-2">
                <Code2 className="w-4 h-4" />
                <span className="text-sm font-medium">Implementation Details</span>
              </div>
              {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {/* Plan details */}
            {showDetails && (
              <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-600 text-sm space-y-2">
                {plan.steps && plan.steps.length > 0 && (
                  <div>
                    <p className="font-semibold mb-1">Steps:</p>
                    <ol className="list-decimal list-inside space-y-1">
                      {plan.steps.map((step: any, idx: number) => (
                        <li key={idx} className="text-xs text-gray-600 dark:text-gray-300">
                          {step.description}
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                {plan.code_preview && (
                  <div>
                    <p className="font-semibold mb-1">Code Preview:</p>
                    <pre className="bg-gray-900 text-green-400 p-3 rounded overflow-x-auto text-xs">
                      <code>{plan.code_preview.code || 'Code will be generated...'}</code>
                    </pre>
                  </div>
                )}

                {plan.affected_files && plan.affected_files.length > 0 && (
                  <div>
                    <p className="font-semibold mb-1">Affected Files:</p>
                    <ul className="list-disc list-inside text-xs text-gray-600 dark:text-gray-300">
                      {plan.affected_files.map((file: string, idx: number) => (
                        <li key={idx}>{file}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Action buttons */}
            {requiresApproval && (
              <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-600 flex items-center gap-2">
                <Button
                  onClick={handleApply}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm py-2"
                >
                  <Check className="w-4 h-4 mr-1" />
                  Apply
                </Button>
                <Button
                  onClick={() => setShowRefineInput(!showRefineInput)}
                  variant="outline"
                  className="flex-1 text-sm py-2"
                >
                  <Edit2 className="w-4 h-4 mr-1" />
                  Refine
                </Button>
                <Button
                  onClick={handleReject}
                  variant="outline"
                  className="flex-1 border-red-300 text-red-600 hover:bg-red-50 text-sm py-2"
                >
                  <X className="w-4 h-4 mr-1" />
                  Reject
                </Button>
              </div>
            )}

            {/* Refinement input */}
            {showRefineInput && (
              <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-600">
                <textarea
                  value={refineInput}
                  onChange={(e) => setRefineInput(e.target.value)}
                  placeholder="Describe how you'd like to refine this plan..."
                  className="w-full rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={2}
                />
                <div className="flex gap-2 mt-2">
                  <Button onClick={handleRefine} className="flex-1 bg-purple-600 hover:bg-purple-700 text-sm py-1">
                    Send Refinement
                  </Button>
                  <Button
                    onClick={() => {
                      setShowRefineInput(false);
                      setRefineInput('');
                    }}
                    variant="outline"
                    className="text-sm py-1"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <p className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
