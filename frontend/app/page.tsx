"use client";

import { ChatWindow } from "./components/ChatWindow";

export default function Home() {
  const agentCoreUrl = process.env.NEXT_PUBLIC_AGENTCORE_URL || "";
  const agentCoreApiKey = process.env.NEXT_PUBLIC_AGENTCORE_API_KEY || "";

  if (!agentCoreUrl) {
    return (
      <div className="flex items-center justify-center h-screen bg-solaris-gray-light">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-solaris-dark mb-4">
            Configuration Required
          </h1>
          <p className="text-solaris-gray-dark">
            Please set NEXT_PUBLIC_AGENTCORE_URL environment variable
          </p>
        </div>
      </div>
    );
  }

  return <ChatWindow apiUrl={agentCoreUrl} apiKey={agentCoreApiKey} />;
}
