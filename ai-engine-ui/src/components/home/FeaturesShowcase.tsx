'use client';

import { AnimatedSection } from '../shared/AnimatedSection';
import { Bug, Zap, Shield, Cpu } from 'lucide-react';

const features = [
  {
    icon: Bug,
    title: 'Intelligent Bug Detection',
    description: 'Real-time monitoring that catches errors before they impact production',
  },
  {
    icon: Zap,
    title: 'Automated Fixes',
    description: 'AI-powered code generation that resolves issues automatically',
  },
  {
    icon: Shield,
    title: 'Build Validation',
    description: 'Comprehensive testing before deployment to ensure code quality',
  },
  {
    icon: Cpu,
    title: 'Smart Analysis',
    description: 'Deep learning algorithms that understand your codebase patterns',
  },
];

export function FeaturesShowcase() {
  return (
    <section className="relative py-32 px-4 bg-black">
      {/* Background Watermark */}
      <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 opacity-5 pointer-events-none">
        <h2 className="text-[12vw] font-bold uppercase tracking-wider text-white text-center select-none">
          ENGINE
        </h2>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Section Header */}
        <AnimatedSection className="text-center mb-20">
          <h2 className="text-5xl md:text-6xl font-bold uppercase tracking-tighter text-white mb-6">
            Powerful <span className="text-premium-gradient italic">Capabilities</span>
          </h2>
          <p className="text-xl text-zinc-400 max-w-2xl mx-auto font-light">
            Engineered for precision. Built for scale. Optimized for autonomous performance.
          </p>
        </AnimatedSection>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <AnimatedSection key={feature.title} delay={index * 0.1}>
              <div className="group h-full premium-card p-8 transition-all duration-500 hover:-translate-y-1">
                <div className="w-12 h-12 mb-8 bg-white/5 border border-white/10 rounded-full flex items-center justify-center group-hover:bg-white group-hover:border-white transition-all duration-500">
                  <feature.icon className="h-5 w-5 text-white group-hover:text-black transition-colors" />
                </div>
                
                <h3 className="text-xl font-bold text-white mb-4 uppercase tracking-tighter">
                  {feature.title}
                </h3>
                
                <p className="text-zinc-400 text-sm leading-relaxed">
                  {feature.description}
                </p>

                <div className="mt-8 pt-6 border-t border-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <a
                    href="#"
                    className="inline-flex items-center space-x-2 text-white text-xs font-bold uppercase tracking-widest"
                  >
                    <span>View Docs</span>
                    <span className="group-hover:translate-x-1 transition-transform">→</span>
                  </a>
                </div>
              </div>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </section>
  );
}
