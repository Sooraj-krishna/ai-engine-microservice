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
  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = 'unset';
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-md z-[100]"
          />

          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-full w-full md:w-96 z-[101]"
          >
            <div className="h-full bg-black/90 backdrop-blur-2xl border-r border-white/5 p-8 flex flex-col overflow-y-auto custom-scrollbar">
              <div className="flex justify-between items-center mb-12 flex-shrink-0">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                    <span className="text-black font-black text-[8px]">AI</span>
                  </div>
                  <span className="text-white font-black tracking-widest text-xs">MENU</span>
                </div>
                <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-all">
                  <X className="h-5 w-5 text-zinc-500" />
                </button>
              </div>

              <nav className="flex-1 space-y-2 mb-8">
                {menuItems.map((item, index) => (
                  <motion.div
                    key={item.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Link
                      href={item.href}
                      onClick={onClose}
                      className="group flex items-center space-x-4 p-4 rounded-xl hover:bg-white/5 transition-all border border-transparent hover:border-white/5"
                    >
                      <item.icon className="h-5 w-5 text-zinc-500 group-hover:text-white transition-colors" />
                      <span className="text-zinc-400 group-hover:text-white text-sm font-bold uppercase tracking-widest transition-colors">
                        {item.name}
                      </span>
                    </Link>
                  </motion.div>
                ))}
              </nav>

              <div className="mt-auto pt-8 border-t border-white/5 flex-shrink-0">
                <Link
                  href="/analysis"
                  onClick={onClose}
                  className="block w-full py-4 bg-white text-black text-center text-xs font-black uppercase tracking-[0.2em] rounded-full hover:bg-zinc-200 transition-all shadow-[0_0_20px_-5px_rgba(255,255,255,0.3)]"
                >
                  Start Analysis
                </Link>
                <p className="mt-8 text-[10px] text-zinc-600 uppercase tracking-widest font-bold text-center">
                  AI Engine Core v2.0
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
