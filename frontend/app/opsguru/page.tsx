"use client";
/* eslint-disable tailwindcss/no-custom-classname */
/* eslint-disable tailwindcss/no-arbitrary-value */

import Image from "next/image";
import Link from "next/link";
import { Space_Grotesk, Inter } from "next/font/google";
import { ChatWindow } from "../components/ChatWindow";

const ogHeading = Space_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-og-heading",
  display: "swap",
});

const ogBody = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-og-body",
  display: "swap",
});

export default function OpsGuruDemo() {
  const agentCoreUrl = process.env.NEXT_PUBLIC_AGENTCORE_URL || "";
  const agentCoreApiKey = process.env.NEXT_PUBLIC_AGENTCORE_API_KEY || "";

  if (!agentCoreUrl) {
    return (
      <div
        className={`${ogHeading.variable} ${ogBody.variable} flex min-h-screen items-center justify-center bg-[#010816] text-opsguru-text font-[var(--font-og-body)]`}
      >
        <div className="max-w-md space-y-4 text-center">
          <h1 className="text-3xl font-[var(--font-og-heading)] tracking-tight">Configuration Required</h1>
          <p className="text-opsguru-text/70">
            Please set NEXT_PUBLIC_AGENTCORE_URL (and optional NEXT_PUBLIC_AGENTCORE_API_KEY) to use the OpsGuru Operator Assistant demo.
          </p>
          <Link
            href="/"
            className="inline-flex items-center justify-center rounded-full border border-white/20 px-5 py-2 text-sm uppercase tracking-[0.2em] text-opsguru-text hover:border-opsguru-accent"
          >
            Return to Solaris Demo
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`${ogHeading.variable} ${ogBody.variable} flex min-h-screen flex-col bg-opsguru-background text-opsguru-text font-[var(--font-og-body)]`}
    >
      <header className="sticky top-0 z-30 w-full border-b border-white/10 bg-[#030b1f]/95 backdrop-blur">
        <div className="mx-auto flex w-full max-w-6xl items-center gap-4 px-5 py-4">
          <div className="flex items-center justify-start pl-6">
            <Image src="/opsguru-logo-white.png" alt="OpsGuru Operator Assistant" width={360} height={80} priority className="h-16 w-auto" />
          </div>
          <div className="flex-1 text-center space-y-0.5">
            <p className="text-base uppercase tracking-[0.4em] text-white/70">Operator Assistant</p>
            <p className="font-[var(--font-og-heading)] text-3xl tracking-[0.22em] text-white">
              Knowledge & Response Suite
            </p>
          </div>
        </div>
      </header>

      <main className="flex-1 bg-gradient-to-b from-[#010814] via-[#041431] to-[#010612]">
        <div className="mx-auto w-full max-w-5xl px-5 py-10 lg:py-14">
          <section className="relative overflow-hidden rounded-[32px] border border-white/35 bg-gradient-to-br from-[#1c3561] via-[#24477b] to-[#2f5690] px-6 py-12 shadow-[0_35px_95px_rgba(0,0,0,0.55)] sm:px-12">
            <div className="pointer-events-none absolute -left-24 top-6 h-64 w-64 rounded-full bg-white/35 blur-[160px]" />
            <div className="pointer-events-none absolute right-0 top-0 h-48 w-48 rounded-full bg-[#7ee3ff]/40 blur-[140px]" />
            <div className="relative space-y-8">
              <div className="space-y-5 text-left">
                <span className="inline-flex items-center gap-3 rounded-full border border-white/50 bg-white/25 px-4 py-1 text-xs uppercase tracking-[0.35em] text-[#041634]">
                  <span className="h-2 w-2 rounded-full bg-[#0f6aa8]" />
                  Live Session
                </span>
                <h2 className="font-[var(--font-og-heading)] text-4xl leading-tight text-white md:text-5xl">
                  AI-guided maintenance for OpsGuru power systems.
                </h2>
                <p className="text-base leading-relaxed text-white/90 drop-shadow-[0_1px_12px_rgba(0,0,0,0.45)]">
                  Ask operational questions, review cited documentation, and stay grounded in verified technical knowledge. Surface troubleshooting steps, alarm thresholds, and documentation insights in seconds. The Operator Assistant keeps your crews aligned with the latest manuals and operational practices.
                </p>
                <div className="h-2" />
              </div>

              <div className="rounded-[40px] border border-[#dbe5fb] bg-white flex min-h-[520px] flex-col shadow-[0_30px_80px_rgba(3,11,21,0.3)] overflow-hidden">
                <ChatWindow apiUrl={agentCoreUrl} apiKey={agentCoreApiKey} variant="opsguru" />
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="border-t border-white/15 bg-[#030818]/95">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-2 px-5 py-6 text-xs text-white/70 sm:flex-row sm:items-center sm:justify-between">
          <span>© 2025 OpsGuru, a Carbon60 Company. All rights reserved.</span>
          <div className="flex flex-wrap gap-4 uppercase tracking-[0.2em] text-white/65">
            <span>Privacy</span>
            <span>Terms</span>
            <span>Support</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
