import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/layout/Navigation";
import { ScrollProgress } from "@/components/shared/ScrollProgress";
import { MouseBlur } from "@/components/shared/MouseBlur";

const inter = Inter({ subsets: ["latin"] });

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
      <body className={`${inter.className} antialiased`}>
        <MouseBlur />
        <ScrollProgress />
        <Navigation />
        {children}
      </body>
    </html>
  );
}
