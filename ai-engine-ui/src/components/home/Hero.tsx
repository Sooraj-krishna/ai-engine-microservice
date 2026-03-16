'use client';

import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';
import { Sparkles, Zap, ArrowRight, Bug, Shield, Cpu, Target, Lightbulb } from 'lucide-react';
import { CardStack, CardStackItem } from '@/components/ui/card-stack';
import type { BeamsProps } from '@/components/ui/ethereal-beams-hero';

const Beams = dynamic(
  () => import('@/components/ui/ethereal-beams-hero').then((mod) => mod.Beams),
  { ssr: false }
);

// ============================================================================
// SHIMMER BUTTON (matching provided hero style)
// ============================================================================
interface ShimmerButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'sm' | 'lg';
  children: React.ReactNode;
  href?: string;
}

function ShimmerButton({ variant = 'default', size = 'sm', className = '', children, href, ...props }: ShimmerButtonProps) {
  const baseClasses =
    'inline-flex items-center justify-center font-bold uppercase tracking-wider transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20 disabled:pointer-events-none disabled:opacity-50';

  const variants = {
    default: 'bg-white text-black hover:bg-gray-100',
    outline: 'border border-white/20 bg-white/5 backdrop-blur-xl text-white hover:bg-white/10 hover:border-white/30',
    ghost: 'text-white/90 hover:text-white hover:bg-white/10',
  };

  const sizes = {
    sm: 'h-9 px-4 py-2 text-sm',
    lg: 'px-8 py-4 text-base',
  };

  const classes = `group relative overflow-hidden rounded-full ${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`;

  if (href) {
    return (
      <a href={href} className={classes}>
        <span className="relative z-10 flex items-center">{children}</span>
        <div className="absolute inset-0 -top-2 -bottom-2 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
      </a>
    );
  }

  return (
    <button className={classes} {...props}>
      <span className="relative z-10 flex items-center">{children}</span>
      <div className="absolute inset-0 -top-2 -bottom-2 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
    </button>
  );
}

// ============================================================================
// FEATURE CARDS DATA
// ============================================================================
const features = [
  {
    icon: Bug,
    title: 'Bug Detection',
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

// ============================================================================
// MAIN HERO COMPONENT
// ============================================================================
export function Hero() {
  return (
    <div className="relative w-full overflow-hidden bg-black">
      {/* ===== 3D BEAMS BACKGROUND ===== */}
      <div className="fixed inset-0 z-0">
        <Beams
          beamWidth={2.5}
          beamHeight={18}
          beamNumber={15}
          lightColor="#ffffff"
          speed={2.5}
          noiseIntensity={2}
          scale={0.15}
          rotation={43}
        />
      </div>

      {/* Gradient Overlays for readability */}
      <div className="fixed inset-0 z-[1] bg-gradient-to-t from-black/60 via-transparent to-black/30 pointer-events-none" />

      {/* ===== HERO SECTION ===== */}
      <section className="relative z-10 min-h-screen flex items-center justify-center">
        <div className="relative text-center px-4 max-w-5xl mx-auto">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-8 inline-flex items-center rounded-full bg-white/5 backdrop-blur-xl border border-white/10 px-4 py-2 text-sm text-white/90"
          >
            <Sparkles className="mr-2 h-4 w-4 text-white" />
            <span className="font-bold uppercase tracking-wider">Autonomous Intelligence</span>
          </motion.div>

          {/* Main Heading */}
          <motion.h1
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mb-6 text-5xl sm:text-7xl lg:text-8xl font-bold tracking-tight text-white"
          >
            <span className="block">AI</span>
            <span className="block bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
              ENGINE
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mb-10 text-lg sm:text-xl lg:text-2xl text-white/70 max-w-3xl mx-auto leading-relaxed"
          >
            Self-maintaining microservice intelligence that{' '}
            <span className="text-white font-semibold">monitors</span>,{' '}
            <span className="text-white font-semibold">analyzes</span>, and{' '}
            <span className="text-white font-semibold">fixes</span> your codebase automatically
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
          >
            <ShimmerButton size="lg" href="/analysis" className="shadow-2xl shadow-white/10 font-semibold">
              <Zap className="mr-2 h-5 w-5" />
              Start Analyzing
            </ShimmerButton>
            <ShimmerButton variant="outline" size="lg" href="/features" className="font-semibold bg-transparent">
              Explore Features
              <ArrowRight className="ml-2 h-5 w-5" />
            </ShimmerButton>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto"
          >
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-1">100%</div>
              <div className="text-white/40 text-sm uppercase tracking-wider">Automated</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-1">24/7</div>
              <div className="text-white/40 text-sm uppercase tracking-wider">Monitoring</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-1">∞</div>
              <div className="text-white/40 text-sm uppercase tracking-wider">Possibilities</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== FEATURES SECTION ===== */}
      <section className="relative z-10 py-24 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-4 tracking-tight">
              Powerful{' '}
              <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
                Features
              </span>
            </h2>
            <p className="text-lg text-white/50 max-w-2xl mx-auto">
              Built to handle the complexities of modern software development
            </p>
          </motion.div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <div className="group h-full rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6 hover:border-white/20 hover:bg-white/[0.08] transition-all duration-300">
                  <div className="w-14 h-14 mb-5 rounded-xl bg-white/10 border border-white/10 flex items-center justify-center">
                    <feature.icon className="h-7 w-7 text-white/80" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2 uppercase tracking-wide">
                    {feature.title}
                  </h3>
                  <p className="text-white/50 text-sm leading-relaxed">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== ABOUT SECTION ===== */}
      <section className="relative z-10 py-24 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-4 tracking-tight">
              About{' '}
              <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
                AI Engine
              </span>
            </h2>
            <p className="text-lg text-white/50 max-w-2xl mx-auto">
              The future of autonomous software maintenance
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5 }}
            >
              <div className="h-full rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-8 hover:border-white/20 transition-all duration-300">
                <Target className="h-10 w-10 text-white/70 mb-5" />
                <h3 className="text-2xl font-bold text-white mb-3 uppercase tracking-wide">Our Mission</h3>
                <p className="text-white/50 leading-relaxed">
                  To revolutionize software development by providing intelligent, autonomous systems
                  that eliminate manual maintenance overhead and enable developers to focus on innovation.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5 }}
            >
              <div className="h-full rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-8 hover:border-white/20 transition-all duration-300">
                <Lightbulb className="h-10 w-10 text-white/70 mb-5" />
                <h3 className="text-2xl font-bold text-white mb-3 uppercase tracking-wide">Our Vision</h3>
                <p className="text-white/50 leading-relaxed">
                  A world where software maintains itself, automatically detecting and resolving issues
                  before they impact users, powered by advanced AI and machine learning.
                </p>
              </div>
            </motion.div>
          </div>

          {/* Technology Philosophy */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="max-w-4xl mx-auto rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-10 text-center hover:border-white/20 transition-all duration-300">
              <h3 className="text-2xl font-bold text-white uppercase tracking-wider mb-4">
                Technology Philosophy
              </h3>
              <p className="text-white/50 leading-relaxed">
                We believe that the best software is software that maintains itself. By leveraging
                cutting-edge AI, machine learning, and predictive analytics, AI Engine doesn&apos;t just
                detect problems—it understands your codebase, learns from patterns, and evolves with
                your project to provide increasingly intelligent solutions over time.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== CTA / CONTACT SECTION ===== */}
      <section className="relative z-10 py-24 px-4 mb-24">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.6 }}
          >
            <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-12 md:p-16">
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-4 tracking-tight">
                Ready to{' '}
                <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
                  Automate
                </span>
                ?
              </h2>

              <p className="text-lg text-white/50 mb-10 max-w-2xl mx-auto">
                Join the future of software development with AI-powered maintenance
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <ShimmerButton size="lg" href="/analysis" className="shadow-2xl shadow-white/10 font-semibold">
                  Get Started Now
                  <ArrowRight className="ml-2 h-5 w-5" />
                </ShimmerButton>
                <ShimmerButton variant="outline" size="lg" href="mailto:support@aiengine.dev" className="font-semibold bg-transparent">
                  Contact Us
                </ShimmerButton>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
