"use client";

import { ChatWindow } from "./components/ChatWindow";

export default function Home() {
  // Get API URL from environment variable or use default
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";
  const apiKey = process.env.NEXT_PUBLIC_API_KEY || "";

  if (!apiUrl) {
    return (
      <div className="flex items-center justify-center h-screen bg-solaris-gray-light">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-solaris-dark mb-4">
            Configuration Required
          </h1>
          <p className="text-solaris-gray-dark">
            Please set NEXT_PUBLIC_API_URL environment variable
          </p>
        </div>
      </div>
    );
  }

  return <ChatWindow apiUrl={apiUrl} apiKey={apiKey} />;
}
