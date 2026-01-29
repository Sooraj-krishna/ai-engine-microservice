'use client';

import { AnimatedSection } from '../shared/AnimatedSection';
import { Bug, Zap, Shield, Cpu } from 'lucide-react';

const features = [
  {
    icon: Bug,
    title: 'Intelligent Bug Detection',
    description: 'Real-time monitoring that catches errors before they impact production',
    color: 'red',
  },
  {
    icon: Zap,
    title: 'Automated Fixes',
    description: 'AI-powered code generation that resolves issues automatically',
    color: 'yellow',
  },
  {
    icon: Shield,
    title: 'Build Validation',
    description: 'Comprehensive testing before deployment to ensure code quality',
    color: 'blue',
  },
  {
    icon: Cpu,
    title: 'Smart Analysis',
    description: 'Deep learning algorithms that understand your codebase patterns',
    color: 'purple',
  },
];

export function FeaturesShowcase() {
  return (
    <section className="relative py-32 px-4">
      {/* Background Watermark */}
      <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 opacity-5 pointer-events-none">
        <h2 className="text-[12vw] font-bold uppercase tracking-wider text-white text-center">
          FEATURES
        </h2>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Section Header */}
        <AnimatedSection className="text-center mb-20">
          <h2 className="text-5xl md:text-6xl font-bold uppercase tracking-wider text-white mb-6">
            Powerful <span className="text-red-gradient">Features</span>
          </h2>
          <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
            Built to handle the complexities of modern software development
          </p>
        </AnimatedSection>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <AnimatedSection key={feature.title} delay={index * 0.1}>
              <div className="group h-full dark-card rounded-lg p-6 hover:border-cyan-700/50 smooth-transition">
                <div className={`w-16 h-16 mb-6 bg-${feature.color}-950/30 border border-${feature.color}-800/50 rounded-lg flex items-center justify-center`}>
                  <feature.icon className={`h-8 w-8 text-${feature.color}-500`} />
                </div>
                
                <h3 className="text-xl font-bold text-white mb-3 uppercase tracking-wide">
                  {feature.title}
                </h3>
                
                <p className="text-zinc-400">
                  {feature.description}
                </p>

                <div className="mt-6 opacity-0 group-hover:opacity-100 transition-opacity">
                  <a
                    href="/features"
                    className="inline-flex items-center space-x-2 text-cyan-400 hover:text-cyan-400 text-sm font-bold uppercase tracking-wider"
                  >
                    <span>Learn More</span>
                    <span>→</span>
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
