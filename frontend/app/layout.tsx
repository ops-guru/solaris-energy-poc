import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Solaris Energy Operator Assistant",
  description:
    "AI-powered troubleshooting and documentation assistant for gas turbine operators",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
