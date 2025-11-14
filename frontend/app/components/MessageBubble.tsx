"use client";

import { useState } from "react";
import { Message } from "./ChatWindow";

type Variant = "solaris" | "opsguru";

interface MessageBubbleProps {
  message: Message;
  onFollowUp?: (question: string) => void;
  variant?: Variant;
}

const BUBBLE_THEME: Record<
  Variant,
  {
    userBubble: string;
    assistantBubble: string;
    toggleUser: string;
    toggleAssistant: string;
    citationUser: string;
    citationAssistant: string;
    citationLink: string;
    followupLabel: string;
    followupButton: string;
    metadataUser: string;
    metadataAssistant: string;
    confidenceTrackUser: string;
    confidenceTrackAssistant: string;
  }
> = {
  solaris: {
    userBubble:
      "border-solaris-user bg-solaris-user text-white shadow-md",
    assistantBubble:
      "border-solaris-border bg-white text-solaris-charcoal",
    toggleUser: "text-white/90",
    toggleAssistant: "text-solaris-charcoal",
    citationUser: "text-white/85",
    citationAssistant: "text-solaris-charcoal/80",
    citationLink: "text-solaris-accent",
    followupLabel: "text-solaris-charcoal",
    followupButton:
      "px-3 py-1 text-xs text-solaris-accent border border-solaris-border rounded-full bg-solaris-card hover:border-solaris-accent hover:text-solaris-charcoal focus-visible:outline focus-visible:outline-offset-2 focus-visible:outline-solaris-accent transition-colors",
    metadataUser: "text-white/85",
    metadataAssistant: "text-solaris-charcoal/70",
    confidenceTrackUser: "bg-white/30",
    confidenceTrackAssistant: "bg-solaris-border",
  },
  opsguru: {
    userBubble:
      "border-transparent bg-gradient-to-r from-[#0f6aa8] to-[#58bfff] text-white shadow-lg",
    assistantBubble:
      "border-[#ced9f0] bg-[#eef2fb] text-[#0b1c34] shadow-md",
    toggleUser: "text-white/90",
    toggleAssistant: "text-[#0b1c34]/80",
    citationUser: "text-white/90",
    citationAssistant: "text-[#0b1c34]/75",
    citationLink: "text-opsguru-accent",
    followupLabel: "text-[#0b1c34]/70",
    followupButton:
      "px-3 py-1 text-xs text-[#0b1c34] border border-[#dbe3fb] rounded-full bg-white hover:border-opsguru-accent hover:text-opsguru-accent focus-visible:outline focus-visible:outline-offset-2 focus-visible:outline-opsguru-accent transition-colors",
    metadataUser: "text-white/80",
    metadataAssistant: "text-[#0b1c34]/65",
    confidenceTrackUser: "bg-white/45",
    confidenceTrackAssistant: "bg-[#dbe3fb]",
  },
};

export function MessageBubble({
  message,
  onFollowUp,
  variant = "solaris",
}: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [sourcesExpanded, setSourcesExpanded] = useState(false);
  const theme = BUBBLE_THEME[variant];

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-3xl rounded-2xl border shadow-sm p-5 ${
          isUser ? theme.userBubble : theme.assistantBubble
        }`}
      >
        <div className="whitespace-pre-wrap text-base leading-relaxed">{message.content}</div>

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-opacity-20 border-current">
            <button
              type="button"
              onClick={() => setSourcesExpanded((prev) => !prev)}
              className={`text-xs font-semibold mb-2 flex items-center gap-2 ${
                isUser ? theme.toggleUser : theme.toggleAssistant
              }`}
            >
              {sourcesExpanded ? "Hide sources" : "Show sources"}
              <span className="text-[10px]">
                {sourcesExpanded ? "▲" : "▼"}
              </span>
            </button>
            {sourcesExpanded && (
              <ul className="space-y-1">
                {message.citations.map((citation, idx) => (
                  <li
                    key={idx}
                    className={`text-xs ${
                      isUser ? theme.citationUser : theme.citationAssistant
                    }`}
                  >
                    <div className="flex flex-col space-y-1">
                      <div>
                        <span className="font-medium mr-1">{idx + 1}.</span>
                        {citation.url ? (
                          <a
                            href={citation.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`underline ${theme.citationLink}`}
                          >
                            {citation.source}
                          </a>
                        ) : (
                          citation.source
                        )}
                        {citation.page && ` (Page ${citation.page})`}
                        {citation.relevance_score !== undefined && (
                          <span
                            className={`ml-2 ${
                              isUser
                                ? "text-white/75"
                                : "text-solaris-charcoal/60"
                            }`}
                          >
                            ({Math.round(citation.relevance_score * 100)}% match)
                          </span>
                        )}
                      </div>
                      {citation.excerpt && (
                        <p
                          className={`italic ${
                            isUser ? theme.citationUser : theme.citationAssistant
                          }`}
                        >
                          “{citation.excerpt}”
                        </p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Follow-up Suggestions */}
        {message.follow_up_suggestions &&
          message.follow_up_suggestions.length > 0 &&
          !isUser && (
            <div className="mt-4 pt-4 border-t border-opacity-20 border-current">
              <p className={`text-xs font-semibold mb-2 ${theme.followupLabel}`}>
                Suggested follow-ups:
              </p>
              <div className="flex flex-wrap gap-2">
                {message.follow_up_suggestions.map((suggestion, idx) => (
                  <button
                    key={`${suggestion}-${idx}`}
                    type="button"
                    onClick={() => onFollowUp?.(suggestion)}
                    className={theme.followupButton}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

        {/* Metadata */}
        <div
          className={`mt-3 pt-3 border-t border-opacity-20 border-current flex items-center justify-between text-xs ${
            isUser ? theme.metadataUser : theme.metadataAssistant
          }`}
        >
          <div>
            {message.turbine_model && (
              <span className="mr-3">
                Turbine: <span className="font-semibold">{message.turbine_model}</span>
              </span>
            )}
            {message.timestamp && (
              <span>
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            )}
          </div>
          {message.confidence_score !== undefined && (
            <div className="flex items-center space-x-1">
              <span>Confidence:</span>
              <div className="flex items-center space-x-1">
                <div
                  className={`w-16 h-2 rounded-full ${
                    isUser ? theme.confidenceTrackUser : theme.confidenceTrackAssistant
                  }`}
                >
                  <div
                    className={`h-2 rounded-full ${
                      message.confidence_score > 0.7
                        ? "bg-green-500"
                        : message.confidence_score > 0.4
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                    style={{
                      width: `${message.confidence_score * 100}%`,
                    }}
                  ></div>
                </div>
                <span className="font-semibold">
                  {Math.round(message.confidence_score * 100)}%
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
