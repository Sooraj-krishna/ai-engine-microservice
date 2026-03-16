'use client';

import { useEffect } from 'react';
import { X, Home as HomeIcon, BarChart2, History as HistoryIcon, Settings, Bug } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';

interface MenuOverlayProps {
  isOpen: boolean;
  onClose: () => void;
}

const menuItems = [
  { name: 'Home', href: '/', icon: HomeIcon },
  { name: 'Analysis', href: '/analysis', icon: BarChart2 },
  { name: 'Bug Review', href: '/bugs', icon: Bug },
  { name: 'History', href: '/history', icon: HistoryIcon },
  { name: 'Settings', href: '/settings', icon: Settings },
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
            <div className="h-full bg-black/40 backdrop-blur-xl border-r border-white/10 shadow-2xl shadow-white/5">
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-6 right-6 p-2 rounded-full bg-white/5 border border-white/10 hover:border-white/20 text-white transition-all group"
                aria-label="Close menu"
              >
                <X className="h-5 w-5 text-white group-hover:rotate-90 transition-transform duration-300" />
              </button>

              {/* Menu content */}
              <div className="flex flex-col h-full px-8 py-12">
                {/* Logo/Header */}
                <div className="mb-12">
                  <h2 className="text-2xl font-bold uppercase tracking-wider text-white">
                    Menu
                  </h2>
                  <div className="h-0.5 w-16 bg-gradient-to-r from-white to-transparent mt-2" />
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
                        <div className="flex items-center gap-3 px-4 py-3 rounded-full bg-white/5 border border-transparent hover:border-white/20 hover:bg-white/10 transition-all duration-300">
                          <item.icon className="h-5 w-5 text-white/70" />
                          <span className="text-white text-lg font-semibold uppercase tracking-wide group-hover:text-white/90 transition-colors">
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
                    className="block w-full px-6 py-4 bg-white text-black hover:bg-gray-100 font-bold uppercase tracking-wider text-center rounded-full shadow-lg transition-all transform hover:scale-105"
                  >
                    Start Analyzing
                  </Link>
                </motion.div>

                {/* Footer info */}
                <div className="mt-6 pt-6 border-t border-white/10">
                  <p className="text-xs text-white/30 uppercase tracking-wider">
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
