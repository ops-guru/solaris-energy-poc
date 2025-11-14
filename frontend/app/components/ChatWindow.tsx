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

type Variant = "solaris" | "opsguru";

interface ChatWindowProps {
  apiUrl: string;
  apiKey?: string;
  variant?: Variant;
}

const VARIANT_CONFIG: Record<
  Variant,
  {
    sessionKey: string;
    welcomeMessage: string;
    clearedMessage: string;
    headerWrapper: string;
    headerTitleClass: string;
    headerSubtitleClass: string;
    eyebrow: string;
    subtitle: string;
    clearButtonClasses: string;
    chatBodyBg: string;
    loadingBubble: string;
    loadingMessage: string;
    loadingTextClass: string;
    loadingDotsWrapper: string;
    loadingDot: string;
    inputWrapper: string;
  }
> = {
  solaris: {
    sessionKey: "solaris_session_id",
    welcomeMessage:
      "Welcome to the Solaris Energy Operator Assistant. I can help you troubleshoot issues, find procedures, and answer questions about your turbines. How can I assist you today?",
    clearedMessage: "Session cleared. How can I assist you today?",
    headerWrapper: "border-b border-solaris-border/80 bg-white/80 px-6 py-5",
    headerTitleClass:
      "font-display text-xl text-solaris-charcoal uppercase tracking-[0.32em]",
    headerSubtitleClass: "text-sm text-solaris-charcoal/65",
    eyebrow: "Operator Assistant Console",
    subtitle:
      "Ask questions, review sourced answers, and stay aligned with Solaris documentation.",
    clearButtonClasses:
      "inline-flex items-center gap-2 rounded-full border border-solaris-border px-4 py-2 text-xs uppercase tracking-[0.28em] text-solaris-accent hover:border-solaris-accent",
    chatBodyBg: "bg-[#F6F4EF]",
    loadingBubble:
      "max-w-3xl rounded-2xl border border-solaris-border bg-solaris-card px-4 py-5 text-sm shadow-sm",
    loadingMessage:
      "Solaris assistant is reviewing the manuals for you…",
    loadingTextClass: "text-solaris-charcoal/80",
    loadingDotsWrapper: "text-solaris-accent",
    loadingDot: "bg-solaris-accent",
    inputWrapper: "border-t border-solaris-border/80 bg-white/80 px-6 py-5",
  },
  opsguru: {
    sessionKey: "opsguru_session_id",
    welcomeMessage:
      "Welcome to the Operator Assistant. I can help you troubleshoot issues, find procedures, and answer questions about your power systems. How can I assist you today?",
    clearedMessage: "Session cleared. How can I assist you today?",
    headerWrapper:
      "border-b border-[#dbe5fb] bg-white px-6 py-5 shadow-sm",
    headerTitleClass:
      "font-display text-xl text-[#0b1c34] uppercase tracking-[0.32em]",
    headerSubtitleClass: "text-sm text-[#4a5d7a]",
    eyebrow: "Operator Assistant Console",
    subtitle:
      "Ask questions, review sourced answers, and stay aligned with technical documentation.",
    clearButtonClasses:
      "inline-flex items-center gap-2 rounded-full border border-[#dbe5fb] px-4 py-2 text-xs uppercase tracking-[0.28em] text-[#0b1c34] hover:border-opsguru-accent hover:text-opsguru-accent",
    chatBodyBg: "bg-white",
    loadingBubble:
      "max-w-3xl rounded-2xl border border-[#dfe7fb] bg-white px-4 py-5 text-sm shadow-lg text-[#0b1c34]",
    loadingMessage: "Operator Assistant is reviewing the manuals for you…",
    loadingTextClass: "text-[#0b1c34]/80",
    loadingDotsWrapper: "text-[#0f6aa8]",
    loadingDot: "bg-opsguru-accent",
    inputWrapper:
      "border-t border-[#dfe7fb] bg-white px-6 py-5",
  },
};

export function ChatWindow({ apiUrl, apiKey, variant = "solaris" }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const config = VARIANT_CONFIG[variant];

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
      content: config.welcomeMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages([welcomeMessage]);
  }, [variant, config.welcomeMessage]);

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
        localStorage.setItem(config.sessionKey, nextSessionId);
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
      localStorage.removeItem(config.sessionKey);
      setMessages([
        {
          role: "assistant",
          content: config.clearedMessage,
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
    const storedSessionId = localStorage.getItem(config.sessionKey);
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      setSessionId(null);
    }
  }, [config.sessionKey]);

  return (
    <div className="flex h-full flex-col">
      <header className={config.headerWrapper}>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className={config.headerTitleClass}>
              {config.eyebrow}
            </h2>
            <p className={config.headerSubtitleClass}>
              {config.subtitle}
            </p>
          </div>
          {sessionId && (
            <button
              onClick={handleClearSession}
              className={config.clearButtonClasses}
            >
              Clear Session
            </button>
          )}
        </div>
      </header>

      <div className={`flex-1 overflow-y-auto ${config.chatBodyBg}`}>
        <div className="space-y-4 px-6 py-6">
          {messages.map((message, index) => (
            <MessageBubble
              key={index}
              message={message}
              onFollowUp={handleFollowUpSelect}
              variant={variant}
            />
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className={config.loadingBubble}>
                <p className={`mb-3 ${config.loadingTextClass}`}>{config.loadingMessage}</p>
                <div className={`flex items-center gap-2 ${config.loadingDotsWrapper}`}>
                  <span className={`h-2.5 w-2.5 animate-bounce rounded-full ${config.loadingDot}`} />
                  <span
                    className={`h-2.5 w-2.5 animate-bounce rounded-full ${config.loadingDot}`}
                    style={{ animationDelay: "0.15s" }}
                  />
                  <span
                    className={`h-2.5 w-2.5 animate-bounce rounded-full ${config.loadingDot}`}
                    style={{ animationDelay: "0.3s" }}
                  />
                </div>
              </div>
            </div>
          )}
          {error && (
            <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-red-700">
              {error}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className={config.inputWrapper}>
        <InputBox onSend={handleSendMessage} disabled={isLoading} variant={variant} />
      </div>
    </div>
  );
}
