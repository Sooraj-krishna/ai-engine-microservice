'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export function LoadingScreen() {
  const [loading, setLoading] = useState(true);

  return (
    <AnimatePresence>
      {loading && (
        <motion.div
          id="loading-screen"
          initial={{ opacity: 1 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          onAnimationComplete={() => {
            // This is handled by AnimatePresence exit
          }}
          className="fixed inset-0 z-[200] bg-black flex items-center justify-center overflow-hidden"
        >
          {/* Subtle Grid Background */}
          <div className="absolute inset-0 opacity-[0.03]" 
               style={{ backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)', backgroundSize: '30px 30px' }} />
          
          <div className="relative">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 1 }}
              className="text-center"
            >
              <div className="w-16 h-16 mx-auto bg-white rounded-full flex items-center justify-center mb-12 relative">
                <div className="absolute inset-0 bg-white blur-2xl opacity-20 animate-pulse" />
                <span className="text-black font-black text-xl relative z-10">AI</span>
              </div>
              
              <h1 className="text-2xl font-black text-white uppercase tracking-[0.5em] mb-4">
                AI ENGINE
              </h1>
              
              <div className="flex flex-col items-center">
                <div className="text-4xl font-black text-white italic tracking-tighter mb-4">
                  <LoadingCounter onComplete={() => setTimeout(() => setLoading(false), 500)} />
                </div>
                
                <div className="h-[1px] w-48 bg-white/10 relative overflow-hidden">
                  <motion.div 
                    initial={{ x: '-100%' }}
                    animate={{ x: '100%' }}
                    transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent"
                  />
                </div>
                
                <p className="mt-6 text-[10px] text-zinc-500 uppercase tracking-[0.3em] font-bold">
                  Synchronizing Neural Pipelines
                </p>
              </div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function LoadingCounter({ onComplete }: { onComplete: () => void }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCount((prev) => {
        const next = prev + Math.floor(Math.random() * 20) + 5;
        if (next >= 100) {
          clearInterval(interval);
          onComplete();
          return 100;
        }
        return next;
      });
    }, 120);

    return () => clearInterval(interval);
  }, [onComplete]);

  return <>{Math.min(count, 100)}%</>;
}
