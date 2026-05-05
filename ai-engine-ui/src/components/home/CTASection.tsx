'use client';

import { AnimatedSection } from '../shared/AnimatedSection';
import { ArrowRight } from 'lucide-react';

export function CTASection() {
  return (
    <section className="relative py-32 px-4 bg-black overflow-hidden">
      {/* Background Decorative Element */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-white/[0.02] rounded-full blur-[120px] pointer-events-none" />
      
      <div className="max-w-4xl mx-auto text-center relative z-10">
        <AnimatedSection>
          <div className="premium-card p-12 md:p-20">
            <h2 className="text-4xl md:text-5xl lg:text-7xl font-bold uppercase tracking-tighter text-white mb-8">
              Ready to <span className="text-premium-gradient italic">Automate</span>?
            </h2>
            
            <p className="text-xl text-zinc-400 mb-12 max-w-2xl mx-auto font-light leading-relaxed">
              Experience the pinnacle of engineering intelligence. Join the elite teams scaling with autonomous maintenance.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
              <a
                href="/analysis"
                className="shimmer-button w-full sm:w-auto"
              >
                <span>Get Started Now</span>
              </a>

              <a
                href="#"
                className="glass-button w-full sm:w-auto"
              >
                <span>Request Demo</span>
              </a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-12 mt-20 pt-12 border-t border-white/5">
              <div>
                <div className="text-4xl font-bold text-white mb-2 tracking-tighter">100%</div>
                <div className="text-[10px] text-zinc-500 uppercase tracking-[0.2em] font-bold">Automated</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-white mb-2 tracking-tighter"> 24/7</div>
                <div className="text-[10px] text-zinc-500 uppercase tracking-[0.2em] font-bold">Monitoring</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-white mb-2 tracking-tighter">∞</div>
                <div className="text-[10px] text-zinc-500 uppercase tracking-[0.2em] font-bold">Scale</div>
              </div>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </section>
  );
}
