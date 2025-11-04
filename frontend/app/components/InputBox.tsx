"use client";

import { useState, KeyboardEvent } from "react";

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function InputBox({ onSend, disabled }: InputBoxProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-end space-x-3">
      <div className="flex-1">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about turbine operation, troubleshooting, or procedures..."
          disabled={disabled}
          rows={1}
          className="w-full px-4 py-3 border border-solaris-gray-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-solaris-primary focus:border-transparent resize-none disabled:bg-solaris-gray-light disabled:cursor-not-allowed"
          style={{
            minHeight: "48px",
            maxHeight: "120px",
          }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = "auto";
            target.style.height = `${Math.min(target.scrollHeight, 120)}px`;
          }}
        />
        <p className="text-xs text-solaris-gray-dark mt-1 ml-1">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
      <button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        className="px-6 py-3 bg-solaris-primary text-white rounded-lg font-semibold hover:bg-opacity-90 disabled:bg-solaris-gray-medium disabled:cursor-not-allowed disabled:opacity-50 transition-colors shadow-sm"
      >
        Send
      </button>
    </div>
  );
}
