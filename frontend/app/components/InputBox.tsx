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
    <div className="flex items-end gap-3 flex-wrap sm:flex-nowrap">
      <div className="flex-1">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about turbine operation, troubleshooting, or procedures..."
          disabled={disabled}
          rows={1}
          className="w-full rounded-xl border border-solaris-border bg-solaris-card px-4 py-3 text-solaris-charcoal focus:border-solaris-accent focus:outline-none focus:ring-2 focus:ring-solaris-accent/40 disabled:cursor-not-allowed disabled:bg-solaris-surface"
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
        <p className="mt-1 ml-1 text-xs text-solaris-charcoal/55">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
      <button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        className="rounded-xl border border-solaris-charcoal bg-solaris-charcoal px-6 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-white shadow-md transition-colors hover:bg-black disabled:border-solaris-border disabled:bg-solaris-border disabled:text-solaris-charcoal/50 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </div>
  );
}
