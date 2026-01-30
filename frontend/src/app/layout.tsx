import type { Metadata } from "next";
import { Suspense } from "react";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/header";
import { Magnifier } from "@/components/Magnifier";
import { Providers } from "@/components/providers";

// Compact, highly readable body font
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

// Elegant serif for display headings
const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "VRD.ai - Veteran Resource Directory",
  description:
    "Find employment, training, housing, and legal resources for Veterans nationwide. Aggregating resources from VA.gov, DOL, and community sources.",
  keywords: ["veterans", "resources", "employment", "housing", "legal", "training", "VA"],
  openGraph: {
    title: "VRD.ai - Veteran Resource Directory",
    description: "Find employment, training, housing, and legal resources for Veterans nationwide.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${playfair.variable} ${inter.variable}`}>
      <body className="min-h-screen bg-background font-body antialiased">
        <Providers>
          <Suspense>
            <Header />
          </Suspense>
          <Suspense>
            <Magnifier />
          </Suspense>
          {children}
        </Providers>
      </body>
    </html>
  );
}
