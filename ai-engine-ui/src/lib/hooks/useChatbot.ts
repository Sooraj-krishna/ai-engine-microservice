import { useState, useEffect, useCallback } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    message_type?: string;
    intent?: string;
    has_plan?: boolean;
    [key: string]: any;
  };
}

interface Session {
  session_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  conversation_history: Message[];
  context: {
    current_intent: string | null;
    pending_changes: string[];
    related_features: any[];
  };
  metadata: {
    message_count: number;
    last_intent: string | null;
  };
}

interface ChatResponse {
  success: boolean;
  response: string;
  intent?: string;
  plan?: any;
  change_id?: string;
  requires_approval?: boolean;
  error?: string;
}

interface PendingChange {
  change_id: string;
  session_id: string;
  status: string;
  plan: {
    plan_id: string;
    summary: string;
    steps: any[];
    estimated_effort: string;
    complexity: string;
    affected_files: string[];
    code_preview?: any;
  };
  intent: string;
  user_request: string;
}

const API_BASE = 'http://localhost:8000';

export function useChatbot(sessionId?: string) {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(sessionId || null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [pendingChanges, setPendingChanges] = useState<PendingChange[]>([]);

  // Create a new session
  const createNewSession = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/chat/session/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'default' })
      });
      
      const data = await response.json();
      
      if (data.success && data.session) {
        setCurrentSessionId(data.session.session_id);
        setMessages(data.session.conversation_history || []);
        localStorage.setItem('chatbot_session_id', data.session.session_id);
        return data.session;
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  }, []);

  // Load an existing session
  const loadSession = useCallback(async (sid: string) => {
    try {
      const response = await fetch(`${API_BASE}/chat/session/${sid}`);
      const data = await response.json();
      
      if (data.success && data.session) {
        setCurrentSessionId(sid);
        setMessages(data.session.conversation_history || []);
        return data.session;
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  }, []);

  // Send a message
  const sendMessage = useCallback(async (message: string) => {
    if (!currentSessionId || !message.trim()) return;

    setIsLoading(true);

    // Add user message optimistically
    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await fetch(`${API_BASE}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId,
          message
        })
      });

      const data: ChatResponse = await response.json();

      if (data.success) {
        // Add assistant response
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString(),
          metadata: {
            intent: data.intent,
            has_plan: !!data.plan,
            change_id: data.change_id,
            requires_approval: data.requires_approval,
            plan: data.plan
          }
        };
        setMessages(prev => [...prev, assistantMessage]);

        // If there's a pending change, fetch updated pending changes
        if (data.change_id) {
          await fetchPendingChanges();
        }
      } else {
        // Show error message
        const errorMessage: Message = {
          role: 'assistant',
          content: data.error || 'Sorry, something went wrong. Please try again.',
          timestamp: new Date().toISOString(),
          metadata: { message_type: 'error' }
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Failed to send message. Please check your connection.',
        timestamp: new Date().toISOString(),
        metadata: { message_type: 'error' }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [currentSessionId]);

  // Fetch pending changes
  const fetchPendingChanges = useCallback(async () => {
    if (!currentSessionId) return;

    try {
      const response = await fetch(`${API_BASE}/chat/pending-changes/${currentSessionId}`);
      const data = await response.json();

      if (data.success) {
        setPendingChanges(data.pending_changes || []);
      }
    } catch (error) {
      console.error('Failed to fetch pending changes:', error);
    }
  }, [currentSessionId]);

  // Apply a change
  const applyChange = useCallback(async (changeId: string) => {
    if (!currentSessionId) return;

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat/apply-change`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          change_id: changeId,
          session_id: currentSessionId
        })
      });

      const data = await response.json();

      if (data.success) {
        // Refresh messages to get the execution result
        await loadSession(currentSessionId);
        await fetchPendingChanges();
        return data;
      }
    } catch (error) {
      console.error('Failed to apply change:', error);
    } finally {
      setIsLoading(false);
    }
  }, [currentSessionId, loadSession, fetchPendingChanges]);

  // Reject a change
  const rejectChange = useCallback(async (changeId: string, reason?: string) => {
    if (!currentSessionId) return;

    try {
      const response = await fetch(`${API_BASE}/chat/reject-change`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          change_id: changeId,
          session_id: currentSessionId,
          reason
        })
      });

      const data = await response.json();

      if (data.success) {
        // Refresh messages
        await loadSession(currentSessionId);
        await fetchPendingChanges();
        return data;
      }
    } catch (error) {
      console.error('Failed to reject change:', error);
    }
  }, [currentSessionId, loadSession, fetchPendingChanges]);

  // Request refinement (send a follow-up message)
  const requestRefinement = useCallback(async (refinementMessage: string) => {
    return sendMessage(refinementMessage);
  }, [sendMessage]);

  // Initialize: load session from localStorage or create new
  useEffect(() => {
    const initSession = async () => {
      const savedSessionId = localStorage.getItem('chatbot_session_id');
      
      if (savedSessionId) {
        const session = await loadSession(savedSessionId);
        if (!session) {
          // Session not found, create new
          await createNewSession();
        }
      } else {
        await createNewSession();
      }
    };

    if (!currentSessionId) {
      initSession();
    }
  }, [currentSessionId, loadSession, createNewSession]);

  // Fetch pending changes when session changes
  useEffect(() => {
    if (currentSessionId) {
      fetchPendingChanges();
    }
  }, [currentSessionId, fetchPendingChanges]);

  return {
    sessionId: currentSessionId,
    messages,
    isLoading,
    pendingChanges,
    sendMessage,
    createNewSession,
    loadSession,
    applyChange,
    rejectChange,
    requestRefinement,
    fetchPendingChanges
  };
}
