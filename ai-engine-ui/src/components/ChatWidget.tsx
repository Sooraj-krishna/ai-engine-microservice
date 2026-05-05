'use client';

import { useState, useEffect, useRef } from 'react';
import { API_BASE_URL } from '@/lib/config';
import { Send, X, MessageCircle, Check, XCircle, RefreshCw, Terminal } from 'lucide-react';

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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isExternallyOpened) {
      setIsOpen(true);
      if (externalSessionId) {
        setSessionId(externalSessionId);
        loadSessionHistory(externalSessionId);
      }
    }
  }, [isExternallyOpened, externalSessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSessionHistory = async (sid: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/session/${sid}`);
      if (response.ok) {
        const data = await response.json();
        if (data.messages) setMessages(data.messages);
      }
    } catch (error) {
      console.error('[ChatWidget] Error:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    const userMessage: Message = { role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, session_id: sessionId })
      });
      const data = await response.json();
      if (data.session_id && !sessionId) setSessionId(data.session_id);

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response || data.message || 'No response',
        timestamp: new Date().toISOString(),
        metadata: { plan_id: data.plan_id, requires_approval: data.requires_approval, status: data.status }
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'system', content: '❌ Connection failed.', timestamp: new Date().toISOString() }]);
    } finally {
      setIsLoading(false);
    }
  };

  const approvePlan = async (planId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_id: planId, session_id: sessionId })
      });
      const data = await response.json();
      setMessages(prev => [...prev, {
        role: 'system',
        content: data.message || '✅ Approved.',
        timestamp: new Date().toISOString(),
        metadata: { pr_url: data.pr_url, status: data.status }
      }]);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-8 right-8 w-16 h-16 bg-white text-black rounded-full shadow-[0_0_50px_rgba(255,255,255,0.2)] hover:scale-110 transition-all duration-500 flex items-center justify-center z-40 group"
        >
          <div className="absolute inset-0 bg-white blur-xl opacity-0 group-hover:opacity-20 transition-opacity" />
          <MessageCircle className="w-6 h-6 relative z-10" />
        </button>
      )}

      {isOpen && (
        <div className="fixed bottom-8 right-8 w-[400px] h-[600px] flex flex-col z-[100] premium-card">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-white/5">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white/5 rounded-full flex items-center justify-center">
                <Terminal className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="text-xs font-black uppercase tracking-[0.3em] text-white">Logic Core</h3>
                <p className="text-[9px] text-zinc-500 uppercase tracking-widest">
                  {sessionId ? `ID: ${sessionId.slice(0, 8)}` : 'New Uplink'}
                </p>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="p-2 hover:bg-white/5 rounded-full transition-all">
              <X className="w-4 h-4 text-zinc-500" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
            {messages.length === 0 && (
              <div className="text-center py-20">
                <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6">
                  <MessageCircle className="w-5 h-5 text-zinc-700" />
                </div>
                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-600">Protocol Initialized</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-5 py-4 ${
                  msg.role === 'user' ? 'bg-white text-black' : 
                  msg.role === 'system' ? 'bg-zinc-900 text-zinc-400 border border-white/5' : 
                  'bg-white/5 text-zinc-300 border border-white/10'
                }`}>
                  <p className="text-xs font-medium leading-relaxed">{msg.content}</p>
                  
                  {msg.metadata?.requires_approval && msg.metadata?.plan_id && (
                    <div className="mt-4 flex gap-2">
                      <button
                        onClick={() => approvePlan(msg.metadata!.plan_id!)}
                        className="px-4 py-2 bg-white text-black rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-zinc-200"
                      >
                        Authorize
                      </button>
                    </div>
                  )}

                  {msg.metadata?.pr_url && (
                    <a href={msg.metadata.pr_url} target="_blank" className="mt-4 inline-block text-[10px] font-black uppercase tracking-widest underline decoration-white/20 hover:decoration-white transition-all">
                      View Delta →
                    </a>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-6 border-t border-white/5">
            <div className="relative flex items-center">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="EXECUTE COMMAND..."
                className="w-full bg-white/5 border border-white/10 text-white rounded-full px-6 py-4 text-[10px] font-black uppercase tracking-[0.2em] focus:outline-none focus:border-white/30 placeholder:text-zinc-700"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="absolute right-2 p-3 bg-white text-black rounded-full hover:bg-zinc-200 transition-all disabled:opacity-50"
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
