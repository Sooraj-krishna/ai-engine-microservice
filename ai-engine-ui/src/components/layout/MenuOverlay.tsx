'use client';

import { useEffect } from 'react';
import { X, Home as HomeIcon, Info, List, BarChart2, History as HistoryIcon, Mail, Settings, Bug } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';

interface MenuOverlayProps {
  isOpen: boolean;
  onClose: () => void;
}

const menuItems = [
  { name: 'Home', href: '/', icon: HomeIcon },
  { name: 'About', href: '/about', icon: Info },
  { name: 'Features', href: '/features', icon: List },
  { name: 'Analysis', href: '/analysis', icon: BarChart2 },
  { name: 'Bug Review', href: '/bugs', icon: Bug },
  { name: 'History', href: '/history', icon: HistoryIcon },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Contact', href: '/contact', icon: Mail },
];

export function MenuOverlay({ isOpen, onClose }: MenuOverlayProps) {
  // Lock body scroll when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
          />

          {/* Left-side glass menu panel */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed left-0 top-0 h-full w-80 z-[101]"
          >
            {/* Glassmorphism container */}
            <div className="h-full bg-black/40 backdrop-blur-xl border-r border-cyan-500/20 shadow-2xl shadow-cyan-500/10">
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-6 right-6 p-2 rounded-lg bg-zinc-900/50 border border-zinc-700 hover:border-cyan-500/50 text-white transition-all group"
                aria-label="Close menu"
              >
                <X className="h-5 w-5 text-cyan-400 group-hover:rotate-90 transition-transform duration-300" />
              </button>

              {/* Menu content */}
              <div className="flex flex-col h-full px-8 py-12">
                {/* Logo/Header */}
                <div className="mb-12">
                  <h2 className="text-2xl font-bold uppercase tracking-wider text-cyan-400">
                    Menu
                  </h2>
                  <div className="h-0.5 w-16 bg-gradient-to-r from-cyan-500 to-transparent mt-2" />
                </div>

                {/* Navigation items */}
                <nav className="flex-1 space-y-2">
                  {menuItems.map((item, index) => (
                    <motion.div
                      key={item.name}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Link
                        href={item.href}
                        onClick={onClose}
                        className="block group"
                      >
                        <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-zinc-900/30 border border-transparent hover:border-cyan-500/30 hover:bg-cyan-950/20 transition-all duration-300">
                          <item.icon className="h-5 w-5 text-cyan-400" />
                          <span className="text-white text-lg font-semibold uppercase tracking-wide group-hover:text-cyan-400 transition-colors">
                            {item.name}
                          </span>
                        </div>
                      </Link>
                    </motion.div>
                  ))}
                </nav>

                {/* CTA Button */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="mt-auto"
                >
                  <Link
                    href="/analysis"
                    onClick={onClose}
                    className="block w-full px-6 py-4 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-cyan-500 hover:to-teal-400 text-white font-bold uppercase tracking-wider text-center rounded-lg shadow-lg shadow-cyan-950/50 transition-all transform hover:scale-105"
                  >
                    Start Analyzing
                  </Link>
                </motion.div>

                {/* Footer info */}
                <div className="mt-6 pt-6 border-t border-zinc-700/50">
                  <p className="text-xs text-zinc-500 uppercase tracking-wider">
                    AI Engine v2.0
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
