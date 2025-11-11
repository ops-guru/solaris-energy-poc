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
  follow_up_suggestions?: string[];
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
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setIsLoading(true);
    setError(null);

    try {
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (apiKey) {
        headers["x-api-key"] = apiKey;
      }

      const payloadMessages = updatedMessages.map(({ role, content }) => ({
        role,
        content,
      }));

      const response = await fetch(apiUrl, {
        method: "POST",
        headers,
        body: JSON.stringify({
          inputText: query,
          sessionId: sessionId || undefined,
          session_id: sessionId || undefined,
          messages: payloadMessages,
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
        follow_up_suggestions: Array.isArray(data.follow_up_suggestions)
          ? data.follow_up_suggestions.filter((item: unknown): item is string => typeof item === "string" && !!item.trim())
          : [],
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

  const handleFollowUpSelect = (question: string) => {
    if (isLoading) return;
    handleSendMessage(question);
  };

  // Load session ID from localStorage on mount
  useEffect(() => {
    const storedSessionId = localStorage.getItem("solaris_session_id");
    if (storedSessionId) {
      setSessionId(storedSessionId);
    }
  }, []);

  return (
    <div className="flex flex-col min-h-[28rem]">
      <header className="flex items-start justify-between gap-4 px-6 pt-6">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-solaris-teal font-semibold">
            Live session
          </p>
          <h2 className="text-2xl font-display text-solaris-slate">
            Operator Assistant Console
          </h2>
          <p className="text-sm text-solaris-slate/70 mt-1">
            Ask troubleshooting questions and review cited documentation snippets.
          </p>
        </div>
        {sessionId && (
          <button
            onClick={handleClearSession}
            className="whitespace-nowrap px-4 py-2 text-xs font-semibold rounded-full border border-solaris-teal text-solaris-teal hover:bg-white"
          >
            Clear session
          </button>
        )}
      </header>
      <div className="mt-6 flex-1 overflow-y-auto">
        <div className="px-6 pb-6 space-y-4">
          {messages.map((message, index) => (
            <MessageBubble
              key={index}
              message={message}
              onFollowUp={handleFollowUpSelect}
            />
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
      <div className="px-6 pb-6">
        <InputBox onSend={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
