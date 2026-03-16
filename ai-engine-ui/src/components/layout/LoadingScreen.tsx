'use client';

import { motion } from 'framer-motion';

export function LoadingScreen() {
  return (
    <motion.div
      initial={{ opacity: 1 }}
      animate={{ opacity: 0 }}
      transition={{ delay: 2, duration: 0.5 }}
      className="fixed inset-0 z-[200] bg-black flex items-center justify-center"
      style={{ display: 'block' }}
      onAnimationComplete={() => {
        // Hide the loading screen after animation
        setTimeout(() => {
          const element = document.getElementById('loading-screen');
          if (element) element.style.display = 'none';
        }, 100);
      }}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-dot-grid opacity-10" />

      {/* Logo & Counter */}
      <div className="relative text-center">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="w-24 h-24 mx-auto bg-gradient-to-br from-red-600 to-red-700 rounded-lg flex items-center justify-center mb-4">
            <span className="text-white font-bold text-4xl">AI</span>
          </div>
          <h1 className="text-4xl font-bold text-white uppercase tracking-[0.3em]">
            AI ENGINE
          </h1>
        </motion.div>

        {/* Loading Counter */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-6xl font-bold text-cyan-400 font-mono"
        >
          <LoadingCounter />
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-4 text-zinc-500 uppercase tracking-widest text-sm"
        >
          Initializing Intelligence
        </motion.p>
      </div>
    </motion.div>
  );
}

function LoadingCounter() {
  const [count, setCount] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCount((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + Math.floor(Math.random() * 15) + 5;
      });
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return <>{Math.min(count, 100)}%</>;
}

// Need to import React for the counter component
import React from 'react';
