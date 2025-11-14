"use client";

import { useState, KeyboardEvent } from "react";

type Variant = "solaris" | "opsguru";

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  variant?: Variant;
}

const INPUT_VARIANTS: Record<
  Variant,
  {
    placeholder: string;
    textareaClasses: string;
    helperClasses: string;
    buttonEnabled: string;
    buttonDisabled: string;
  }
> = {
  solaris: {
    placeholder:
      "Ask a question about turbine operation, troubleshooting, or procedures...",
    textareaClasses:
      "w-full rounded-xl border border-solaris-border bg-solaris-card px-4 py-3 text-solaris-charcoal focus:border-solaris-accent focus:outline-none focus:ring-2 focus:ring-solaris-accent/40 disabled:cursor-not-allowed disabled:bg-solaris-surface placeholder:text-solaris-charcoal/50",
    helperClasses: "mt-1 ml-1 text-xs text-solaris-charcoal/55",
    buttonEnabled:
      "text-solaris-charcoal cursor-pointer hover:border-solaris-charcoal hover:bg-solaris-charcoal hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white",
    buttonDisabled: "text-solaris-accent/60 cursor-not-allowed",
  },
  opsguru: {
    placeholder: "Ask a question about system operation, troubleshooting, or procedures...",
    textareaClasses:
      "w-full rounded-xl border border-[#dbe3fb] bg-white px-4 py-3 text-[#0b1c34] placeholder:text-[#4a5d7a] focus:border-opsguru-accent focus:outline-none focus:ring-2 focus:ring-opsguru-accent/40 disabled:cursor-not-allowed disabled:bg-[#f3f6ff]",
    helperClasses: "mt-1 ml-1 text-xs text-[#4a5d7a]",
    buttonEnabled:
      "text-white bg-gradient-to-r from-[#0f6aa8] to-[#4fc5ff] border border-transparent cursor-pointer hover:brightness-110 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-opsguru-accent/60",
    buttonDisabled: "text-[#7f8fb0] cursor-not-allowed border-[#dbe3fb] bg-[#f1f5ff]",
  },
};

export function InputBox({ onSend, disabled, variant = "solaris" }: InputBoxProps) {
  const [input, setInput] = useState("");
  const theme = INPUT_VARIANTS[variant];

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

  const isSendDisabled = disabled || !input.trim();
  const baseButtonClasses =
    "rounded-xl border px-6 py-3 text-sm font-semibold uppercase tracking-[0.2em] transition-colors shadow-sm bg-transparent";
  const buttonClasses = isSendDisabled
    ? `${baseButtonClasses} ${theme.buttonDisabled}`
    : `${baseButtonClasses} ${theme.buttonEnabled}`;

  return (
    <div className="flex items-end gap-3 flex-wrap sm:flex-nowrap">
      <div className="flex-1">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={theme.placeholder}
          disabled={disabled}
          rows={1}
          className={theme.textareaClasses}
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
        <p className={theme.helperClasses}>Press Enter to send, Shift+Enter for new line</p>
      </div>
      <button onClick={handleSend} disabled={isSendDisabled} className={buttonClasses}>
        Send
      </button>
    </div>
  );
}
