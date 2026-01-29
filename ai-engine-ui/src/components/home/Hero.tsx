'use client';

import { motion } from 'framer-motion';
import { ChevronDown, Sparkles, Zap } from 'lucide-react';

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-dot-grid opacity-20" />
      
      {/* Large Watermark Text */}
      <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
        <h1 className="text-[20vw] font-bold uppercase tracking-wider text-white">
          ENGINE
        </h1>
      </div>

      {/* Main Content */}
      <div className="relative z-10 text-center px-4 max-w-6xl mx-auto">
        {/* Animated Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-cyan-950/30 border border-cyan-800/50 rounded-full mb-8"
        >
          <Sparkles className="h-4 w-4 text-cyan-400" />
          <span className="text-cyan-400 text-sm font-bold uppercase tracking-wider">
            Autonomous Intelligence
          </span>
        </motion.div>

        {/* Main Heading */}
        <motion.h1
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-6xl md:text-8xl lg:text-9xl font-bold uppercase tracking-wider mb-6"
        >
          <span className="block text-white">AI</span>
          <span className="block text-red-gradient">ENGINE</span>
        </motion.h1>

        {/* Subheading */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-xl md:text-2xl lg:text-3xl text-zinc-400 mb-12 max-w-3xl mx-auto"
        >
          Self-maintaining microservice intelligence that <span className="text-cyan-400 font-bold">monitors</span>, 
          <span className="text-cyan-400 font-bold"> analyzes</span>, and <span className="text-cyan-400 font-bold">fixes</span> your codebase automatically
        </motion.p>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <a
            href="/analysis"
            className="group relative inline-flex items-center space-x-2 px-12 py-4 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-red-600 hover:to-red-500 rounded-lg text-white text-lg font-bold uppercase tracking-wider transition-all shadow-2xl shadow-cyan-950/50 hover:shadow-cyan-900/50 hover:scale-105"
          >
            <Zap className="h-5 w-5" />
            <span>Start Analyzing</span>
          </a>

          <a
            href="/features"
            className="inline-flex items-center space-x-2 px-12 py-4 bg-zinc-900/50 hover:bg-cyan-950/30 border border-zinc-700 hover:border-cyan-800/50 rounded-lg text-white text-lg font-bold uppercase tracking-wider transition-all"
          >
            <span>Explore Features</span>
          </a>
        </motion.div>

        {/* Floating Icons */}
        <motion.div
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -left-20 top-1/4 hidden lg:block"
        >
          <div className="w-24 h-24 bg-cyan-600/10 border border-cyan-600/30 rounded-lg rotate-12 backdrop-blur-sm" />
        </motion.div>

        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -right-20 top-1/3 hidden lg:block"
        >
          <div className="w-32 h-32 bg-purple-600/10 border border-purple-600/30 rounded-lg -rotate-6 backdrop-blur-sm" />
        </motion.div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 1 }}
        className="absolute bottom-12 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="flex flex-col items-center space-y-2"
        >
          <span className="text-zinc-500 text-sm uppercase tracking-wider">Scroll to Explore</span>
          <ChevronDown className="h-6 w-6 text-cyan-400" />
        </motion.div>
      </motion.div>
    </section>
  );
}
