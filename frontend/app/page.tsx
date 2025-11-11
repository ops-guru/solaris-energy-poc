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
      <div className="w-full border-b border-solaris-border bg-solaris-surface/80">
        <div className="mx-auto w-full max-w-6xl px-5 py-6 flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-4">
            <Image
              src="/solaris-logo.png"
              alt="Solaris Energy Infrastructure"
              width={180}
              height={44}
              priority
            />
            <div className="hidden sm:flex sm:flex-col sm:gap-1">
              <span className="font-display text-sm tracking-[0.35em] uppercase text-solaris-accent">
                Operator Assistant
              </span>
              <span className="text-sm text-solaris-charcoal/70">
                Knowledge & Response Suite
              </span>
            </div>
          </div>
          <p className="text-sm text-solaris-charcoal/80 max-w-2xl leading-relaxed">
            Surface troubleshooting steps, alarm thresholds, and documentation insights in seconds.
            The Solaris Operator Assistant keeps your crews aligned with the latest manuals and operational practices.
          </p>
        </div>
      </div>

      <main className="flex-1">
        <div className="mx-auto w-full max-w-6xl px-5 py-8 lg:py-10">
          <section className="grid gap-8 lg:grid-cols-[ minmax(0,1.1fr)_minmax(0,1fr) ]">
            <div className="order-2 lg:order-1 space-y-4">
              <div className="flex flex-col gap-3">
                <span className="font-display text-xs tracking-[0.4em] uppercase text-solaris-accent/80">
                  Live session
                </span>
                <h1 className="font-display text-4xl md:text-5xl text-solaris-charcoal leading-tight">
                  AI-guided maintenance, tuned for Solaris power systems.
                </h1>
                <p className="text-base text-solaris-charcoal/75 leading-relaxed max-w-xl">
                  Ask operational questions, review cited documentation, and stay grounded in verified Solaris knowledge. Designed to match the experience of Solaris’ Power as a Service platform.
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <div className="inline-flex items-center gap-2 rounded-full border border-solaris-border bg-solaris-card px-4 py-2 text-xs uppercase tracking-[0.25em] text-solaris-accent/80">
                  <span className="h-2 w-2 rounded-full bg-solaris-accent" />
                  Operator Console
                </div>
                <div className="inline-flex items-center gap-2 rounded-full border border-solaris-border bg-solaris-card px-4 py-2 text-xs uppercase tracking-[0.25em] text-solaris-accent/80">
                  <span className="h-2 w-2 rounded-full bg-solaris-accentLight" />
                  RAG Enabled
                </div>
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
