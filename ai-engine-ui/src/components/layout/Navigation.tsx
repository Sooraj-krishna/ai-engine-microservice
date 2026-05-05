'use client';

import { useState } from 'react';
import { Menu, X, Github } from 'lucide-react';
import { MenuOverlay } from './MenuOverlay';

export function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <>
      {/* Bottom Floating Navigation Bar */}
      <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
        <div className="bg-black/80 backdrop-blur-2xl border border-white/10 rounded-full px-6 py-3 shadow-[0_0_50px_-12px_rgba(255,255,255,0.2)]">
          <div className="flex items-center space-x-8">
            {/* Logo */}
            <a href="/" className="flex items-center space-x-2 group">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <span className="text-black font-bold text-xs">AI</span>
              </div>
              <span className="text-white font-bold tracking-widest hidden sm:block group-hover:text-zinc-400 transition-colors">
                ENGINE
              </span>
            </a>

            {/* Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center space-x-2 px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-full transition-all group"
            >
              {isMenuOpen ? (
                <X className="h-4 w-4 text-white" />
              ) : (
                <Menu className="h-4 w-4 text-white" />
              )}
              <span className="text-white text-xs font-bold uppercase tracking-widest group-hover:text-zinc-300 transition-colors">
                Menu
              </span>
            </button>

            {/* CTA Button */}
            <a
              href="/analysis"
              className="px-6 py-2 bg-white hover:bg-zinc-200 rounded-full text-black text-xs font-bold uppercase tracking-widest transition-all shadow-lg shadow-white/5"
            >
              Analyze
            </a>
          </div>
        </div>
      </nav>

      {/* Menu Overlay */}
      <MenuOverlay isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />
    </>
  );
}
