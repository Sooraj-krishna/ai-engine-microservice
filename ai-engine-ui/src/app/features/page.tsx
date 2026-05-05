import { AnimatedSection } from '@/components/shared/AnimatedSection';
import { Bug, Zap, Shield, Cpu, GitBranch, Eye, Clock, Check, ChevronRight, ArrowUpRight } from 'lucide-react';

const allFeatures = [
  {
    icon: Bug,
    title: 'Autonomous Detection',
    description: 'Continuously monitors your application for errors, exceptions, and console warnings using deep heuristic analysis.',
    status: 'Core',
    category: 'Analysis',
  },
  {
    icon: Zap,
    title: 'Auto-Fix Pipeline',
    description: 'AI-powered code generation that automatically resolves detected issues with zero human intervention required.',
    status: 'Live',
    category: 'Automation',
  },
  {
    icon: Shield,
    title: 'Validation Engine',
    description: 'Comprehensive testing and validation protocols that ensure every fix meets your performance standards.',
    status: 'Active',
    category: 'Security',
  },
  {
    icon: Cpu,
    title: 'Neural Mapping',
    description: 'Advanced algorithms that build a complete mental model of your codebase for contextual understanding.',
    status: 'Core',
    category: 'Intelligence',
  },
  {
    icon: GitBranch,
    title: 'VCS Synchronization',
    description: 'Seamless integration with GitHub and GitLab for automated branching, commits, and pull requests.',
    status: 'Live',
    category: 'Integrations',
  },
  {
    icon: Eye,
    title: 'Sentinel Monitoring',
    description: '24/7 autonomous monitoring of your production application health and infrastructure performance.',
    status: 'Active',
    category: 'Performance',
  },
  {
    icon: Clock,
    title: 'Temporal Auditing',
    description: 'Complete historical tracking of all analysis runs, giving you a full timeline of codebase evolution.',
    status: 'Active',
    category: 'Analysis',
  },
  {
    icon: Check,
    title: 'Heuristic Scaling',
    description: 'Dynamically scales detection logic based on incoming traffic and application complexity.',
    status: 'Beta',
    category: 'Advanced',
  },
];

export default function FeaturesPage() {
  return (
    <div className="bg-black min-h-screen pt-32 pb-24 px-4 overflow-hidden relative">
      {/* Ambient background effects */}
      <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-white/[0.02] rounded-full blur-[150px] -ml-80 -mt-80 pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-white/[0.01] rounded-full blur-[120px] -mr-60 -mb-60 pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* ── HERO SECTION ───────────────────────────── */}
        <div className="text-center mb-24">
          <AnimatedSection>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full mb-8">
              <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
              <span className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-500">System Capabilities v2.0</span>
            </div>
            <h1 className="text-6xl md:text-8xl font-bold uppercase tracking-tighter text-white mb-8 leading-none">
              Powerful <span className="text-zinc-600 italic">Core</span>
            </h1>
            <p className="text-lg md:text-xl text-zinc-500 font-light max-w-2xl mx-auto leading-relaxed">
              Everything required to maintain your codebase autonomously through advanced heuristic intelligence.
            </p>
          </AnimatedSection>
        </div>

        {/* ── FEATURES GRID ──────────────────────────── */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {allFeatures.map((feature, index) => (
            <AnimatedSection key={feature.title} delay={index * 0.05}>
              <div className="group premium-card p-10 h-full flex flex-col hover:bg-white/[0.03] transition-all duration-500">
                {/* Header */}
                <div className="flex items-start justify-between mb-10">
                  <div className="w-16 h-16 bg-white/[0.03] border border-white/10 rounded-3xl flex items-center justify-center group-hover:scale-110 group-hover:bg-white group-hover:text-black transition-all duration-500">
                    <feature.icon className="h-8 w-8" />
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-lg">
                    <div className="w-1 h-1 rounded-full bg-white opacity-50" />
                    <span className="text-[9px] font-black uppercase tracking-widest text-zinc-500">
                      {feature.status}
                    </span>
                  </div>
                </div>

                {/* Content */}
                <div className="mb-8">
                  <h3 className="text-2xl font-bold text-white mb-4 uppercase tracking-tight">
                    {feature.title}
                  </h3>
                  <p className="text-zinc-500 text-sm leading-relaxed font-light">
                    {feature.description}
                  </p>
                </div>

                {/* Footer */}
                <div className="mt-auto pt-8 border-t border-white/5 flex items-center justify-between">
                  <span className="text-[9px] font-black uppercase tracking-[0.2em] text-zinc-700">
                    {feature.category}
                  </span>
                  <div className="w-8 h-8 rounded-full border border-white/5 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <ArrowUpRight className="h-4 w-4 text-zinc-500" />
                  </div>
                </div>
              </div>
            </AnimatedSection>
          ))}
        </div>

        {/* ── CTA SECTION ────────────────────────────── */}
        <AnimatedSection delay={0.5}>
          <div className="mt-32 p-16 premium-card text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-white/[0.01] pointer-events-none" />
            <h2 className="text-3xl font-bold text-white mb-6 uppercase tracking-tighter">Ready to automate?</h2>
            <p className="text-zinc-500 mb-10 max-w-xl mx-auto font-light">
              Deploy the engine to your repository and let intelligence handle the maintenance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-10 py-5 bg-white text-black text-[10px] font-black uppercase tracking-[0.2em] rounded-full hover:bg-zinc-200 transition-all shadow-[0_0_30px_-5px_rgba(255,255,255,0.3)]">
                Deploy Now
              </button>
              <button className="px-10 py-5 bg-white/5 border border-white/10 text-white text-[10px] font-black uppercase tracking-[0.2em] rounded-full hover:bg-white/10 transition-all">
                View Documentation
              </button>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </div>
  );
}
