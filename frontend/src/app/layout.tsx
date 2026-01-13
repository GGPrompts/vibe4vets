import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vibe4Vets - Veteran Resource Directory",
  description:
    "Find employment, training, housing, and legal resources for veterans nationwide.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
