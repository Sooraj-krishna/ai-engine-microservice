import { AnimatedSection } from '@/components/shared/AnimatedSection';
import { Target, Lightbulb, Rocket, Code } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="page-enter min-h-screen py-24 px-4">
      {/* Hero Section */}
      <div className="relative mb-32">
        <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 opacity-5 pointer-events-none">
          <h1 className="text-[15vw] font-bold uppercase tracking-wider text-white text-center">
            ABOUT
          </h1>
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <AnimatedSection>
            <h1 className="text-5xl md:text-7xl font-bold uppercase tracking-wider text-white mb-6">
              About <span className="text-red-gradient">AI Engine</span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              The future of autonomous software maintenance
            </p>
          </AnimatedSection>
        </div>
      </div>

      {/* Mission & Vision */}
      <div className="max-w-7xl mx-auto mb-24">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <AnimatedSection delay={0.1}>
            <div className="dark-card rounded-lg p-8 h-full">
              <Target className="h-12 w-12 text-cyan-400 mb-6" />
              <h2 className="text-3xl font-bold text-white uppercase tracking-wide mb-4">
                Our Mission
              </h2>
              <p className="text-zinc-400 text-lg leading-relaxed">
                To revolutionize software development by providing intelligent, autonomous systems 
                that eliminate manual maintenance overhead and enable developers to focus on innovation.
              </p>
            </div>
          </AnimatedSection>

          <AnimatedSection delay={0.2}>
            <div className="dark-card rounded-lg p-8 h-full">
              <Lightbulb className="h-12 w-12 text-yellow-500 mb-6" />
              <h2 className="text-3xl font-bold text-white uppercase tracking-wide mb-4">
                Our Vision
              </h2>
              <p className="text-zinc-400 text-lg leading-relaxed">
                A world where software maintains itself, automatically detecting and resolving issues 
                before they impact users, powered by advanced AI and machine learning.
              </p>
            </div>
          </AnimatedSection>
        </div>
      </div>

      {/* Goals */}
      <div className="max-w-7xl mx-auto mb-24">
        <AnimatedSection>
          <h2 className="text-4xl md:text-5xl font-bold text-white uppercase tracking-wider mb-12 text-center">
            Our <span className="text-red-gradient">Goals</span>
          </h2>
        </AnimatedSection>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              icon: Code,
              title: 'Code Quality',
              description: 'Maintain pristine code standards across your entire codebase',
            },
            {
              icon: Rocket,
              title: 'Zero Downtime',
              description: 'Prevent bugs before they reach production environments',
            },
            {
              icon: Target,
              title: 'Efficiency',
              description: 'Reduce manual maintenance time by 90% or more',
            },
            {
              icon: Lightbulb,
              title: 'Innovation',
              description: 'Free your team to focus on building great features',
            },
          ].map((goal, index) => (
            <AnimatedSection key={goal.title} delay={index * 0.1}>
              <div className="dark-card rounded-lg p-6 text-center h-full">
                <div className="w-16 h-16 mx-auto mb-4 bg-cyan-950/30 border border-cyan-800/50 rounded-lg flex items-center justify-center">
                  <goal.icon className="h-8 w-8 text-cyan-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3 uppercase tracking-wide">
                  {goal.title}
                </h3>
                <p className="text-zinc-400">{goal.description}</p>
              </div>
            </AnimatedSection>
          ))}
        </div>
      </div>

      {/* Technology Philosophy */}
      <AnimatedSection>
        <div className="max-w-4xl mx-auto dark-card rounded-lg p-12 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white uppercase tracking-wider mb-6">
            Technology Philosophy
          </h2>
          <p className="text-zinc-400 text-lg leading-relaxed">
            We believe that the best software is software that maintains itself. By leveraging 
            cutting-edge AI, machine learning, and predictive analytics, AI Engine doesn't just 
            detect problems—it understands your codebase, learns from patterns, and evolves with 
            your project to provide increasingly intelligent solutions over time.
          </p>
        </div>
      </AnimatedSection>
    </div>
  );
}
