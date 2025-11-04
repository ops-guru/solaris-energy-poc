"use client";

import { useState, useEffect, useRef } from "react";
import { MessageBubble } from "./MessageBubble";
import { InputBox } from "./InputBox";

export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  citations?: Citation[];
  confidence_score?: number;
  turbine_model?: string;
}

export interface Citation {
  source: string;
  page?: number;
  relevance_score?: number;
}

interface ChatWindowProps {
  apiUrl: string;
  apiKey?: string;
}

export function ChatWindow({ apiUrl, apiKey }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: Message = {
      role: "assistant",
      content:
        "Welcome to the Solaris Energy Operator Assistant. I can help you troubleshoot issues, find procedures, and answer questions about your turbines. How can I assist you today?",
      timestamp: new Date().toISOString(),
    };
    setMessages([welcomeMessage]);
  }, []);

  const handleSendMessage = async (query: string) => {
    if (!query.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: query,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (apiKey) {
        headers["x-api-key"] = apiKey;
      }

      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          query,
          session_id: sessionId || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const data = await response.json();

      // Update session ID if provided
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
        // Store in localStorage
        localStorage.setItem("solaris_session_id", data.session_id);
      }

      const assistantMessage: Message = {
        role: "assistant",
        content: data.response || "I'm sorry, I couldn't generate a response.",
        timestamp: new Date().toISOString(),
        citations: data.citations || [],
        confidence_score: data.confidence_score,
        turbine_model: data.turbine_model,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An error occurred";
      setError(errorMessage);

      const errorResponse: Message = {
        role: "assistant",
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearSession = async () => {
    if (!sessionId) return;

    try {
      const headers: HeadersInit = {};
      if (apiKey) {
        headers["x-api-key"] = apiKey;
      }

      await fetch(`${apiUrl}/chat/${sessionId}`, {
        method: "DELETE",
        headers,
      });

      setSessionId(null);
      localStorage.removeItem("solaris_session_id");
      setMessages([
        {
          role: "assistant",
          content:
            "Session cleared. How can I assist you today?",
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      console.error("Failed to clear session:", err);
    }
  };

  // Load session ID from localStorage on mount
  useEffect(() => {
    const storedSessionId = localStorage.getItem("solaris_session_id");
    if (storedSessionId) {
      setSessionId(storedSessionId);
    }
  }, []);

  return (
    <div className="flex flex-col h-screen bg-solaris-gray-light">
      {/* Header */}
      <header className="bg-white border-b border-solaris-gray-medium shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-solaris-dark">
                Solaris Energy Operator Assistant
              </h1>
              <p className="text-sm text-solaris-gray-dark mt-1">
                Troubleshooting & Documentation Support
              </p>
            </div>
            {sessionId && (
              <button
                onClick={handleClearSession}
                className="px-4 py-2 text-sm text-solaris-gray-dark hover:text-solaris-dark border border-solaris-gray-medium rounded-lg hover:bg-solaris-gray-light transition-colors"
              >
                Clear Session
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-lg shadow-sm p-4 border border-solaris-gray-medium">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-solaris-primary rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-solaris-primary rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                  <div className="w-2 h-2 bg-solaris-primary rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                </div>
              </div>
            </div>
          )}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-solaris-gray-medium shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <InputBox onSend={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
