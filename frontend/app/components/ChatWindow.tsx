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
  excerpt?: string;
  url?: string;
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

      const response = await fetch(apiUrl, {
        method: "POST",
        headers,
        body: JSON.stringify({
          inputText: query,
          sessionId: sessionId || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const data = await response.json();

      const nextSessionId =
        data.sessionId || data.session_id || sessionId || null;
      if (nextSessionId) {
        setSessionId(nextSessionId);
        localStorage.setItem("solaris_session_id", nextSessionId);
      }

      const responseText =
        data.outputText ||
        data.response ||
        data.answer ||
        data.output?.text ||
        data.output?.response ||
        "I'm sorry, I couldn't generate a response.";

      const citations: Citation[] =
        data.citations ||
        data.output?.citations ||
        data.references ||
        [];

      const confidence =
        data.confidenceScore ??
        data.confidence_score ??
        data.output?.confidenceScore ??
        null;

      const turbineModel =
        data.turbine_model || data.turbineModel || data.metadata?.turbine_model;

      const assistantMessage: Message = {
        role: "assistant",
        content: responseText,
        timestamp: new Date().toISOString(),
        citations,
        confidence_score:
          typeof confidence === "number" ? Math.min(Math.max(confidence, 0), 1) : undefined,
        turbine_model: turbineModel,
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
              <h1 className="text-2xl font-bold text-gray-900">
                Solaris Energy Operator Assistant
              </h1>
              <p className="text-sm text-gray-700 mt-1">
                Troubleshooting & Documentation Support
              </p>
            </div>
            {sessionId && (
              <button
                onClick={handleClearSession}
                className="px-4 py-2 text-sm text-gray-800 hover:text-gray-900 border border-solaris-gray-medium rounded-lg hover:bg-solaris-gray-light transition-colors font-medium"
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
              <div className="bg-white rounded-lg shadow-sm p-4 border border-solaris-gray-medium max-w-3xl">
                <p className="text-sm text-gray-700 mb-3">
                  Solaris assistant is reviewing the manuals for you...
                </p>
                <div className="flex items-center space-x-2 text-solaris-primary">
                  <div className="w-2.5 h-2.5 bg-solaris-primary rounded-full animate-bounce"></div>
                  <div
                    className="w-2.5 h-2.5 bg-solaris-primary rounded-full animate-bounce"
                    style={{ animationDelay: "0.15s" }}
                  ></div>
                  <div
                    className="w-2.5 h-2.5 bg-solaris-primary rounded-full animate-bounce"
                    style={{ animationDelay: "0.3s" }}
                  ></div>
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
