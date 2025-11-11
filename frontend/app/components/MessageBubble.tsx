"use client";

import { useState } from "react";
import { Message, Citation } from "./ChatWindow";

interface MessageBubbleProps {
  message: Message;
  onFollowUp?: (question: string) => void;
}

export function MessageBubble({ message, onFollowUp }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [sourcesExpanded, setSourcesExpanded] = useState(false);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-3xl rounded-2xl border shadow-sm p-5 ${
          isUser
            ? "border-solaris-user bg-solaris-user text-white shadow-md"
            : "border-solaris-border bg-white text-solaris-charcoal"
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
                isUser ? "text-white/90" : "text-solaris-charcoal"
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
                      isUser ? "text-white/85" : "text-solaris-charcoal/80"
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
                            className={`underline ${
                              isUser ? "text-white" : "text-solaris-accent"
                            }`}
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
                            isUser ? "text-white/80" : "text-solaris-charcoal/60"
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
              <p className="text-xs font-semibold mb-2 text-solaris-charcoal">
                Suggested follow-ups:
              </p>
              <div className="flex flex-wrap gap-2">
                {message.follow_up_suggestions.map((suggestion, idx) => (
                  <button
                    key={`${suggestion}-${idx}`}
                    type="button"
                    onClick={() => onFollowUp?.(suggestion)}
                    className="px-3 py-1 text-xs text-solaris-accent border border-solaris-border rounded-full bg-solaris-card hover:border-solaris-accent hover:text-solaris-charcoal focus-visible:outline focus-visible:outline-offset-2 focus-visible:outline-solaris-accent transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

        {/* Metadata */}
        <div className={`mt-3 pt-3 border-t border-opacity-20 border-current flex items-center justify-between text-xs ${
          isUser ? "text-white/85" : "text-solaris-charcoal/70"
        }`}>
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
                    isUser ? "bg-white/30" : "bg-solaris-border"
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
