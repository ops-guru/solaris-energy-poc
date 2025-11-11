"use client";

import { ChatWindow } from "./components/ChatWindow";

export default function Home() {
  const agentCoreUrl = process.env.NEXT_PUBLIC_AGENTCORE_URL || "";
  const agentCoreApiKey = process.env.NEXT_PUBLIC_AGENTCORE_API_KEY || "";

  if (!agentCoreUrl) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-solaris-sandLight">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-solaris-slate mb-4">
            Configuration Required
          </h1>
          <p className="text-solaris-slate/70">
            Please set NEXT_PUBLIC_AGENTCORE_URL environment variable
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-solaris-sandLight">
      <header className="bg-white shadow-sm border-b border-solaris-cloud/60">
        <div className="max-w-6xl mx-auto flex items-center justify-between py-5 px-6">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-solaris-teal flex items-center justify-center text-white text-lg font-semibold">
              S
            </div>
            <div>
              <p className="font-display text-lg tracking-wide text-solaris-teal uppercase">
                Solaris Energy Infrastructure
              </p>
              <p className="text-xs text-solaris-slate/70">
                Operator Knowledge & Response Suite
              </p>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-solaris-slate/80">
            <a href="#" className="hover:text-solaris-teal transition-colors">
              Power as a Service
            </a>
            <a href="#" className="hover:text-solaris-teal transition-colors">
              Logistics Solutions
            </a>
            <a href="#" className="hover:text-solaris-teal transition-colors">
              Industry Applications
            </a>
            <a href="#" className="hover:text-solaris-teal transition-colors">
              Investor Relations
            </a>
            <a href="#" className="hover:text-solaris-teal transition-colors">
              Contact
            </a>
          </nav>
          <button className="hidden md:inline-flex items-center rounded-full bg-solaris-gold px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-solaris-gold/90 transition-colors">
            Solaris Software Suite
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 pb-16">
        <section className="grid md:grid-cols-2 gap-16 items-center py-14">
          <div>
            <p className="uppercase tracking-[0.3em] text-xs text-solaris-teal font-semibold mb-3">
              Operator Assistant
            </p>
            <h1 className="font-display text-4xl md:text-5xl text-solaris-slate leading-tight mb-6">
              AI-guided maintenance, tuned for Solaris power systems.
            </h1>
            <p className="text-solaris-slate/80 leading-relaxed mb-8 max-w-xl">
              Surface troubleshooting steps, alarm thresholds, and documentation insights in seconds. The Solaris Operator Assistant keeps your crews aligned with the latest manuals and operational practices.
            </p>
            <div className="flex flex-wrap gap-4">
              <button className="px-6 py-3 rounded-full bg-solaris-teal text-white font-semibold shadow-sm hover:bg-solaris-tealDark transition-colors">
                Launch Assistant
              </button>
              <button className="px-6 py-3 rounded-full border border-solaris-teal text-solaris-teal font-semibold hover:bg-white transition-colors">
                View Documentation
              </button>
            </div>
          </div>
          <div className="relative">
            <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-solaris-teal/10 to-solaris-gold/10 blur-2xl" aria-hidden="true" />
            <div className="relative rounded-3xl border border-solaris-cloud shadow-xl bg-white/90 backdrop-blur">
              <ChatWindow apiUrl={agentCoreUrl} apiKey={agentCoreApiKey} />
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-white border-t border-solaris-cloud/60 text-sm text-solaris-slate/60">
        <div className="max-w-6xl mx-auto px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <span>© {new Date().getFullYear()} Solaris Energy Infrastructure. All rights reserved.</span>
          <div className="flex gap-6">
            <a href="#" className="hover:text-solaris-teal">Privacy</a>
            <a href="#" className="hover:text-solaris-teal">Terms</a>
            <a href="#" className="hover:text-solaris-teal">Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
