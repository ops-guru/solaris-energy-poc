"use client";

import Image from "next/image";
import { ChatWindow } from "./components/ChatWindow";

export default function Home() {
  const agentCoreUrl = process.env.NEXT_PUBLIC_AGENTCORE_URL || "";
  const agentCoreApiKey = process.env.NEXT_PUBLIC_AGENTCORE_API_KEY || "";

  if (!agentCoreUrl) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-solaris-background">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-solaris-charcoal mb-4">
            Configuration Required
          </h1>
          <p className="text-solaris-charcoal/70">
            Please set NEXT_PUBLIC_AGENTCORE_URL environment variable
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-solaris-background">
      <div className="sticky top-0 z-30 w-full border-b border-solaris-border bg-[#EFECE6]">
        <div className="mx-auto w-full max-w-6xl px-5 py-8 flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <Image
            src="/solaris-logo.png"
            alt="Solaris Energy Infrastructure"
            width={220}
            height={52}
            priority
            className="sm:self-start"
          />
          <div className="space-y-2 text-center sm:text-left sm:self-center">
            <span className="font-display text-xs tracking-[0.45em] uppercase text-solaris-accent">
              Operator Assistant
            </span>
            <h1 className="font-display text-3xl sm:text-4xl text-solaris-charcoal tracking-[0.12em] uppercase">
              Knowledge & Response Suite
            </h1>
          </div>
        </div>
      </div>

      <main className="flex-1">
        <div className="mx-auto w-full max-w-6xl px-5 py-8 lg:py-10">
          <section className="grid gap-8 lg:grid-cols-[ minmax(0,1.1fr)_minmax(0,1fr) ]">
            <div className="order-2 lg:order-1 space-y-4">
              <div className="flex flex-col gap-3">
                <span className="font-display text-xs tracking-[0.35em] uppercase text-solaris-accent/80">
                  Live session
                </span>
                <h2 className="font-display text-4xl md:text-5xl text-solaris-charcoal leading-tight">
                  AI-guided maintenance, tuned for Solaris power systems.
                </h2>
                <p className="text-base text-solaris-charcoal/75 leading-relaxed">
                  Ask operational questions, review cited documentation, and stay grounded in verified Solaris knowledge. Surface troubleshooting steps, alarm thresholds, and documentation insights in seconds. The Solaris Operator Assistant keeps your crews aligned with the latest manuals and operational practices.
                </p>
              </div>
            </div>

            <div className="order-1 lg:order-2">
              <div className="rounded-[28px] border border-solaris-border bg-solaris-card shadow-sm overflow-hidden min-h-[480px] flex flex-col">
                <ChatWindow apiUrl={agentCoreUrl} apiKey={agentCoreApiKey} />
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="border-t border-solaris-border bg-solaris-surface/80">
        <div className="mx-auto w-full max-w-6xl px-5 py-6 text-xs text-solaris-charcoal/60 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <span>© {new Date().getFullYear()} Solaris Energy Infrastructure. All rights reserved.</span>
          <div className="flex flex-wrap gap-4 uppercase tracking-[0.2em]">
            <span>Privacy</span>
            <span>Terms</span>
            <span>Support</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
