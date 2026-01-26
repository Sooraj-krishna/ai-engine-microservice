'use client';

import { useState, useEffect, useRef } from 'react';
import { Send, X, MessageCircle, Check, XCircle, RefreshCw } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  metadata?: {
    plan_id?: string;
    requires_approval?: boolean;
    status?: string;
    pr_url?: string;
  };
}

interface ChatWidgetProps {
  externalSessionId?: string | null;
  isExternallyOpened?: boolean;
  onClose?: () => void;
}

export function ChatWidget({ 
  externalSessionId, 
  isExternallyOpened = false,
  onClose 
}: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(isExternallyOpened);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(externalSessionId || null);
  const [pendingPlan, setPendingPlan] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sync with external open state
  useEffect(() => {
    if (isExternallyOpened) {
      setIsOpen(true);
      if (externalSessionId) {
        setSessionId(externalSessionId);
        loadSessionHistory(externalSessionId);
      }
    }
  }, [isExternallyOpened, externalSessionId]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load session history
  const loadSessionHistory = async (sid: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/chatbot/session/${sid}`);
      if (response.ok) {
        const data = await response.json();
        if (data.messages) {
          setMessages(data.messages);
        }
      }
    } catch (error) {
      console.error('[ChatWidget] Error loading session:', error);
    }
  };

  // Send message to chatbot
  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chatbot/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          session_id: sessionId
        })
      });

      const data = await response.json();
      
      // Update session ID if new
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response || data.message || 'No response',
        timestamp: new Date().toISOString(),
        metadata: {
          plan_id: data.plan_id,
          requires_approval: data.requires_approval,
          status: data.status
        }
      };

      setMessages(prev => [...prev, assistantMessage]);

      // If plan requires approval, store it
      if (data.requires_approval && data.plan) {
        setPendingPlan(data.plan);
      }

    } catch (error) {
      console.error('[ChatWidget] Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'system',
        content: '❌ Error connecting to chatbot. Please check if the backend is running.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Approve plan
  const approvePlan = async (planId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/chatbot/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan_id: planId,
          session_id: sessionId
        })
      });

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: data.message || '✅ Plan approved and executing...',
        timestamp: new Date().toISOString(),
        metadata: {
          pr_url: data.pr_url,
          status: data.status
        }
      }]);

      setPendingPlan(null);

    } catch (error) {
      console.error('[ChatWidget] Error approving plan:', error);
      setMessages(prev => [...prev, {
        role: 'system',
        content: '❌ Error approving plan',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Reject plan
  const rejectPlan = (planId: string) => {
    setMessages(prev => [...prev, {
      role: 'user',
      content: '❌ Plan rejected. Please provide more details or try a different approach.',
      timestamp: new Date().toISOString()
    }]);
    setPendingPlan(null);
  };

  const handleClose = () => {
    setIsOpen(false);
    onClose?.();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-lg hover:shadow-2xl transition-all duration-300 flex items-center justify-center hover:scale-110 z-50"
          aria-label="Open AI Chat"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white dark:bg-gray-900 rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-200 dark:border-gray-700">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-2xl">
            <div className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5" />
              <div>
                <h3 className="font-semibold">AI Assistant</h3>
                <p className="text-xs opacity-90">
                  {sessionId ? `Session: ${sessionId.slice(0, 8)}` : 'New conversation'}
                </p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="hover:bg-white/20 p-1 rounded transition-colors"
              aria-label="Close chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-800">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
                <MessageCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Start a conversation with the AI assistant</p>
                <p className="text-sm mt-2">Try: "Change the website font to italic"</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : msg.role === 'system'
                      ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-900 dark:text-yellow-100 border border-yellow-300 dark:border-yellow-700'
                      : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-600'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                  
                  {/* Show approval buttons if plan requires it */}
                  {msg.metadata?.requires_approval && msg.metadata?.plan_id && (
                    <div className="mt-3 flex gap-2">
                      <button
                        onClick={() => approvePlan(msg.metadata!.plan_id!)}
                        disabled={isLoading}
                        className="flex items-center gap-1 px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50"
                      >
                        <Check className="w-4 h-4" />
                        Approve
                      </button>
                      <button
                        onClick={() => rejectPlan(msg.metadata!.plan_id!)}
                        disabled={isLoading}
                        className="flex items-center gap-1 px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50"
                      >
                        <XCircle className="w-4 h-4" />
                        Reject
                      </button>
                    </div>
                  )}

                  {/* Show PR link if available */}
                  {msg.metadata?.pr_url && (
                    <a
                      href={msg.metadata.pr_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 inline-block text-xs underline opacity-75 hover:opacity-100"
                    >
                      View Pull Request →
                    </a>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-700 rounded-2xl px-4 py-2 border border-gray-200 dark:border-gray-600">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white disabled:opacity-50"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Send message"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
