import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "OpsGuru Operator Assistant",
  description:
    "OpsGuru-branded operator assistant for AI-guided maintenance and troubleshooting.",
};

export default function OpsGuruLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

