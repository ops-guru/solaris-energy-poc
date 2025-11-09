"use client";

import { Message, Citation } from "./ChatWindow";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-3xl rounded-lg shadow-sm p-4 ${
          isUser
            ? "bg-solaris-primary text-white"
            : "bg-white border border-solaris-gray-medium text-gray-900"
        }`}
      >
        <div className="whitespace-pre-wrap text-base leading-relaxed">{message.content}</div>

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-opacity-20 border-current">
            <p className={`text-xs font-semibold mb-2 ${
              isUser ? "text-white text-opacity-95" : "text-gray-800"
            }`}>Sources:</p>
            <ul className="space-y-1">
              {message.citations.map((citation, idx) => (
                <li key={idx} className={`text-xs ${
                  isUser ? "text-white text-opacity-90" : "text-gray-700"
                }`}>
                  <div className="flex flex-col space-y-1">
                    <div>
                      <span className="font-medium mr-1">{idx + 1}.</span>
                      {citation.url ? (
                        <a
                          href={citation.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`underline ${
                            isUser ? "text-white" : "text-solaris-primary"
                          }`}
                        >
                          {citation.source}
                        </a>
                      ) : (
                        citation.source
                      )}
                      {citation.page && ` (Page ${citation.page})`}
                      {citation.relevance_score !== undefined && (
                        <span className={`ml-2 ${
                          isUser ? "text-white text-opacity-75" : "text-gray-600"
                        }`}>
                          ({Math.round(citation.relevance_score * 100)}% match)
                        </span>
                      )}
                    </div>
                    {citation.excerpt && (
                      <p
                        className={`italic ${
                          isUser ? "text-white text-opacity-80" : "text-gray-600"
                        }`}
                      >
                        “{citation.excerpt}”
                      </p>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Metadata */}
        <div className={`mt-3 pt-3 border-t border-opacity-20 border-current flex items-center justify-between text-xs ${
          isUser ? "text-white text-opacity-90" : "text-gray-600"
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
                    isUser ? "bg-white bg-opacity-30" : "bg-solaris-gray-medium"
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
