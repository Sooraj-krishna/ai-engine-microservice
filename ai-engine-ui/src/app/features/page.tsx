import { AnimatedSection } from '@/components/shared/AnimatedSection';
import { Bug, Zap, Shield, Cpu, GitBranch, Eye, Clock, Check } from 'lucide-react';

const allFeatures = [
  {
    icon: Bug,
    title: 'Real-time Bug Detection',
    description: 'Continuously monitors your application for errors, exceptions, and console warnings',
    status: 'Active',
    category: 'Analysis',
  },
  {
    icon: Zap,
    title: 'Automated Code Fixes',
    description: 'AI-powered code generation that automatically resolves detected issues',
    status: 'Active',
    category: 'Automation',
  },
  {
    icon: Shield,
    title: 'Build Validation',
    description: 'Comprehensive testing and validation before deployment',
    status: 'Active',
    category: 'Monitoring',
  },
  {
    icon: Cpu,
    title: 'Smart Code Analysis',
    description: 'Deep learning algorithms that understand your codebase patterns',
    status: 'Active',
    category: 'Analysis',
  },
  {
    icon: GitBranch,
    title: 'GitHub Integration',
    description: 'Seamless integration with GitHub for automated pull requests',
    status: 'Active',
    category: 'Automation',
  },
  {
    icon: Eye,
    title: 'Live Monitoring',
    description: '24/7 monitoring of your application health and performance',
    status: 'Active',
    category: 'Monitoring',
  },
  {
    icon: Clock,
    title: 'Analysis History',
    description: 'Complete historical tracking of all analysis runs and fixes',
    status: 'Active',
    category: 'Analysis',
  },
  {
    icon: Check,
    title: 'Feature Requests',
    description: 'AI-powered understanding and implementation of feature requests',
    status: 'Beta',
    category: 'Automation',
  },
];

export default function FeaturesPage() {
  return (
    <div className="page-enter min-h-screen py-24 px-4">
      {/* Hero Section */}
      <div className="relative mb-32">
        <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 opacity-5 pointer-events-none">
          <h1 className="text-[15vw] font-bold uppercase tracking-wider text-white text-center">
            FEATURES
          </h1>
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <AnimatedSection>
            <h1 className="text-5xl md:text-7xl font-bold uppercase tracking-wider text-white mb-6">
              Powerful <span className="text-red-gradient">Features</span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              Everything you need to maintain your codebase autonomously
            </p>
          </AnimatedSection>
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {allFeatures.map((feature, index) => (
            <AnimatedSection key={feature.title} delay={index * 0.05}>
              <div className="group dark-card rounded-lg p-6 h-full hover:border-cyan-700/50 smooth-transition">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="w-14 h-14 bg-cyan-950/30 border border-cyan-800/50 rounded-lg flex items-center justify-center">
                    <feature.icon className="h-7 w-7 text-cyan-400" />
                  </div>
                  <span
                    className={`px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-lg border ${
                      feature.status === 'Active'
                        ? 'bg-green-950/50 text-green-400 border-green-800/50'
                        : 'bg-blue-950/50 text-blue-400 border-blue-800/50'
                    }`}
                  >
                    {feature.status}
                  </span>
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-white mb-3 uppercase tracking-wide">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-zinc-400 mb-4">{feature.description}</p>

                {/* Category Tag */}
                <div className="mt-auto">
                  <span className="inline-block px-3 py-1 bg-zinc-900/50 border border-zinc-800 rounded-lg text-xs text-zinc-500 uppercase tracking-wider">
                    {feature.category}
                  </span>
                </div>
              </div>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </div>
  );
}
