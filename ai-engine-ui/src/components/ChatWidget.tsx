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
          className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-red-600 hover:to-red-500 text-white rounded-full shadow-2xl shadow-cyan-950/50 hover:shadow-cyan-900/50 transition-all duration-300 flex items-center justify-center hover:scale-110 z-40"
          aria-label="Open AI Chat"
        >
          <MessageCircle className="w-7 h-7" />
        </button>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-zinc-950 rounded-lg shadow-2xl shadow-cyan-950/50 flex flex-col z-40 border border-cyan-900/30">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-cyan-900/30 bg-gradient-to-r from-cyan-600 to-teal-500 text-white rounded-t-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                <MessageCircle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold uppercase tracking-wider">AI Assistant</h3>
                <p className="text-xs opacity-75">
                  {sessionId ? `Session: ${sessionId.slice(0, 8)}` : 'New conversation'}
                </p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="hover:bg-white/20 p-2 rounded-lg transition-colors"
              aria-label="Close chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-black/40 scrollbar-thin">
            {messages.length === 0 && (
              <div className="text-center text-zinc-500 mt-8">
                <MessageCircle className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-zinc-400 font-bold uppercase tracking-wider text-sm">Start a Conversation</p>
                <p className="text-xs mt-2 text-zinc-600">Try: "Implement a new feature"</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-cyan-600 to-teal-500 text-white shadow-lg shadow-cyan-950/50'
                      : msg.role === 'system'
                      ? 'bg-yellow-950/30 text-yellow-400 border border-yellow-800/50'
                      : 'bg-zinc-900 text-zinc-100 border border-zinc-800 shadow-lg'
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
                        className="flex items-center gap-1 px-3 py-1 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50"
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
                <div className="bg-zinc-900 rounded-lg px-4 py-3 border border-zinc-800">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-cyan-900/30 bg-zinc-950">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={isLoading}
                className="flex-1 px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 focus:border-cyan-600 placeholder:text-zinc-600 disabled:opacity-50"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="px-4 py-3 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-red-600 hover:to-red-500 text-white rounded-lg hover:shadow-lg shadow-cyan-950/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
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
