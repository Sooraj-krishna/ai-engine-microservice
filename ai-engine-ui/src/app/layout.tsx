import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/layout/Navigation";
import { ScrollProgress } from "@/components/shared/ScrollProgress";

const outfit = Outfit({ 
  subsets: ["latin"],
  variable: "--font-outfit",
});

export const metadata: Metadata = {
  title: "AI Engine - Self-Maintaining Microservice Intelligence",
  description: "Autonomous AI-powered system that monitors, analyzes, and maintains your codebase with intelligent bug detection and automated fixes.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${outfit.variable} font-sans antialiased bg-black text-white`}>
        <ScrollProgress />
        <Navigation />
        {children}
      </body>
    </html>
  );
}
