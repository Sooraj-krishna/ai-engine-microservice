'use client';

import { useState, useEffect, useRef } from 'react';
import { Send, X, MessageCircle, Check, XCircle, RefreshCw, ChevronDown } from 'lucide-react';

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
          className="fixed bottom-6 right-6 bg-white api-border backdrop-blur-md text-black p-4 rounded-full shadow-lg transition-all transform hover:scale-105 border border-white/20 flex items-center justify-center z-40 group"
          aria-label="Open AI Chat"
        >
          <MessageCircle className="h-6 w-6 group-hover:scale-110 transition-transform" />
        </button>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-black/80 backdrop-blur-xl rounded-2xl shadow-2xl flex flex-col z-40 border border-white/10 overflow-hidden animate-in slide-in-from-bottom-10 fade-in duration-300">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center border border-white/10">
                <MessageCircle className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold uppercase tracking-wider text-white text-sm">AI Assistant</h3>
                <p className="text-[10px] text-white/50 uppercase tracking-widest font-bold">
                  {sessionId ? `Session: ${sessionId.slice(0, 8)}` : 'New conversation'}
                </p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="hover:bg-white/10 p-2 rounded-lg transition-colors text-white/60 hover:text-white"
              aria-label="Close chat"
            >
              <ChevronDown className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
            {messages.length === 0 && (
              <div className="text-center mt-8 space-y-4">
                <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto border border-white/10">
                  <MessageCircle className="w-8 h-8 text-white/40" />
                </div>
                <div>
                  <p className="text-white font-bold uppercase tracking-wider text-sm">Start a Conversation</p>
                  <p className="text-xs mt-2 text-white/40">Analyzing your codebase...</p>
                </div>
                <div className="grid gap-2 px-4">
                    <button onClick={() => setInput("Check for pending bugs?")} className="text-xs p-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/60 hover:text-white transition-all text-left">
                        Check for pending bugs?
                    </button>
                    <button onClick={() => setInput("Analyze performance issues")} className="text-xs p-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/60 hover:text-white transition-all text-left">
                        Analyze performance issues
                    </button>
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-white text-black font-medium'
                      : msg.role === 'system'
                      ? 'bg-red-500/10 text-red-200 border border-red-500/20'
                      : 'bg-white/10 text-white border border-white/5'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  
                  {/* Show approval buttons if plan requires it */}
                  {msg.metadata?.requires_approval && msg.metadata?.plan_id && (
                    <div className="mt-4 flex gap-2">
                      <button
                        onClick={() => approvePlan(msg.metadata!.plan_id!)}
                        disabled={isLoading}
                        className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 border border-green-500/20 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors disabled:opacity-50"
                      >
                        <Check className="w-3.5 h-3.5" />
                        Approve
                      </button>
                      <button
                        onClick={() => rejectPlan(msg.metadata!.plan_id!)}
                        disabled={isLoading}
                        className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/20 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors disabled:opacity-50"
                      >
                        <XCircle className="w-3.5 h-3.5" />
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
                      className="mt-2 flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300 font-medium"
                    >
                       <span className="w-1.5 h-1.5 bg-blue-400 rounded-full"></span>
                      View Pull Request
                    </a>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white/5 rounded-2xl px-4 py-3 border border-white/5">
                  <div className="flex gap-1.5">
                    <div className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-1.5 h-1.5 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-white/10 bg-black/40 backdrop-blur-md">
            <div className="flex gap-2 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything..."
                disabled={isLoading}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 text-white rounded-xl focus:outline-none focus:bg-white/10 focus:border-white/20 placeholder:text-white/30 disabled:opacity-50 text-sm transition-all pr-12"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="absolute right-2 top-2 bottom-2 aspect-square flex items-center justify-center bg-white text-black rounded-lg hover:bg-gray-200 transition-all font-bold disabled:opacity-0 disabled:cursor-not-allowed shadow-lg"
                aria-label="Send message"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
