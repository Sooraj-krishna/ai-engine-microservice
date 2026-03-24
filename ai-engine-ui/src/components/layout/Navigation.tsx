'use client';

import { useState } from 'react';
import { Menu, X, ArrowRight } from 'lucide-react';
import { MenuOverlay } from './MenuOverlay';

export function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <>
      {/* Bottom Floating Navigation Bar */}
      <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-full px-6 py-3 shadow-2xl">
          <div className="flex items-center space-x-6">
            {/* Logo */}
            <a href="/" className="flex items-center space-x-2 group">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <span className="text-black font-bold text-sm">AI</span>
              </div>
              <span className="text-white font-bold tracking-wider hidden sm:block group-hover:text-white/80 transition-colors">
                ENGINE
              </span>
            </a>

            {/* Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center space-x-2 px-5 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-full transition-all group"
            >
              {isMenuOpen ? (
                <X className="h-4 w-4 text-white" />
              ) : (
                <Menu className="h-4 w-4 text-white" />
              )}
              <span className="text-white text-sm font-bold uppercase tracking-wider">
                Menu
              </span>
            </button>

            {/* CTA Button */}
            <a
              href="/analysis"
              className="group relative overflow-hidden px-5 py-2 bg-white text-black rounded-full text-sm font-bold uppercase tracking-wider transition-all hover:bg-gray-100"
            >
              <span className="relative z-10 flex items-center">
                Get Started
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </span>
              <div className="absolute inset-0 -top-2 -bottom-2 bg-gradient-to-r from-transparent via-black/10 to-transparent skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
            </a>
          </div>
        </div>
      </nav>

      {/* Menu Overlay */}
      <MenuOverlay isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />
    </>
  );
}
