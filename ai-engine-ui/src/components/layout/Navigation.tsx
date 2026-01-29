'use client';

import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { MenuOverlay } from './MenuOverlay';

export function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <>
      {/* Bottom Floating Navigation Bar */}
      <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
        <div className="bg-zinc-950/90 backdrop-blur-md border border-cyan-900/30 rounded-full px-6 py-3 shadow-2xl shadow-cyan-950/50">
          <div className="flex items-center space-x-8">
            {/* Logo */}
            <a href="/" className="flex items-center space-x-2 group">
              <div className="w-8 h-8 bg-gradient-to-br from-red-600 to-red-700 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <span className="text-white font-bold tracking-wider hidden sm:block group-hover:text-cyan-400 transition-colors">
                ENGINE
              </span>
            </a>

            {/* Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center space-x-2 px-6 py-2 bg-zinc-900/50 hover:bg-cyan-950/50 border border-zinc-800 hover:border-cyan-800/50 rounded-full transition-all group"
            >
              {isMenuOpen ? (
                <X className="h-4 w-4 text-cyan-400" />
              ) : (
                <Menu className="h-4 w-4 text-cyan-400" />
              )}
              <span className="text-white text-sm font-bold uppercase tracking-wider group-hover:text-cyan-400 transition-colors">
                Menu
              </span>
            </button>

            {/* CTA Button */}
            <a
              href="/analysis"
              className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-red-600 hover:to-red-500 rounded-full text-white text-sm font-bold uppercase tracking-wider transition-all shadow-lg shadow-cyan-950/50 hover:shadow-xl hover:shadow-cyan-900/50"
            >
              Get Started
            </a>
          </div>
        </div>
      </nav>

      {/* Menu Overlay */}
      <MenuOverlay isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />
    </>
  );
}
