import type { Metadata } from "next";
import { Suspense } from "react";
import { DM_Serif_Display, Source_Sans_3 } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/header";

const dmSerifDisplay = DM_Serif_Display({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Vibe4Vets - Veteran Resource Directory",
  description:
    "Find employment, training, housing, and legal resources for veterans nationwide. Aggregating resources from VA.gov, DOL, and community sources.",
  keywords: ["veterans", "resources", "employment", "housing", "legal", "training", "VA"],
  openGraph: {
    title: "Vibe4Vets - Veteran Resource Directory",
    description: "Find employment, training, housing, and legal resources for veterans nationwide.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${dmSerifDisplay.variable} ${sourceSans.variable}`}>
      <body className="min-h-screen bg-background font-body antialiased">
        <Suspense>
          <Header />
        </Suspense>
        {children}
      </body>
    </html>
  );
}
