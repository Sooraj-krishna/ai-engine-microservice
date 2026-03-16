'use client';

import { AnimatedSection } from '../shared/AnimatedSection';
import { ArrowRight } from 'lucide-react';

export function CTASection() {
  return (
    <section className="relative py-32 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <AnimatedSection>
          <div className="dark-card rounded-lg p-12 md:p-16">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold uppercase tracking-wider text-white mb-6">
              Ready to <span className="text-red-gradient">Automate</span>?
            </h2>
            
            <p className="text-xl text-zinc-400 mb-10 max-w-2xl mx-auto">
              Join the future of software development with AI-powered maintenance
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href="/analysis"
                className="group inline-flex items-center space-x-2 px-12 py-4 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-red-600 hover:to-red-500 rounded-lg text-white text-lg font-bold uppercase tracking-wider transition-all shadow-2xl shadow-cyan-950/50 hover:shadow-cyan-900/50"
              >
                <span>Get Started Now</span>
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </a>

              <a
                href="/contact"
                className="inline-flex items-center space-x-2 px-12 py-4 bg-transparent hover:bg-zinc-900/50 border border-zinc-700 hover:border-cyan-800/50 rounded-lg text-white text-lg font-bold uppercase tracking-wider transition-all"
              >
                <span>Contact Us</span>
              </a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mt-16 pt-12 border-t border-zinc-800">
              <div>
                <div className="text-4xl font-bold text-cyan-400 mb-2">100%</div>
                <div className="text-sm text-zinc-500 uppercase tracking-wider">Automated</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-cyan-400 mb-2"> 24/7</div>
                <div className="text-sm text-zinc-500 uppercase tracking-wider">Monitoring</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-cyan-400 mb-2">∞</div>
                <div className="text-sm text-zinc-500 uppercase tracking-wider">Possibilities</div>
              </div>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}
