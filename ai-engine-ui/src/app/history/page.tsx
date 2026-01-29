import { AnimatedSection } from '@/components/shared/AnimatedSection';
import { Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function HistoryPage() {
  return (
    <div className="page-enter min-h-screen py-24 px-4">
      {/* Hero Section */}
      <div className="relative mb-32">
        <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 opacity-5 pointer-events-none">
          <h1 className="text-[15vw] font-bold uppercase tracking-wider text-white text-center">
            HISTORY
          </h1>
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <AnimatedSection>
            <h1 className="text-5xl md:text-7xl font-bold uppercase tracking-wider text-white mb-6">
              Analysis <span className="text-red-gradient">History</span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              Track your analysis runs and automated fixes
            </p>
          </AnimatedSection>
        </div>
      </div>

      {/* Placeholder Content */}
      <div className="max-w-4xl mx-auto">
        <AnimatedSection>
          <div className="dark-card rounded-lg p-12 text-center">
            <Clock className="h-16 w-16 text-cyan-400 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-white mb-4 uppercase tracking-wide">
              Coming Soon
            </h2>
            <p className="text-zinc-400 text-lg mb-8">
              This page will display a complete history of all analysis runs, bugs detected, and fixes applied.
            </p>
            <a
              href="/analysis"
              className="inline-block px-8 py-3 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-red-600 hover:to-red-500 rounded-lg text-white font-bold uppercase tracking-wider transition-all shadow-lg shadow-cyan-950/50"
            >
              Start Analysis
            </a>
          </div>
        </AnimatedSection>

        {/* Sample Timeline Preview */}
        <div className="mt-12 space-y-4">
          {[
            { status: 'success', time: '2 hours ago', message: 'Build validation passed' },
            {  status: 'warning', time: '5 hours ago', message: '3 bugs detected and fixed' },
            { status: 'success', time: '1 day ago', message: 'Automated PR merged successfully' },
          ].map((item, index) => (
            <AnimatedSection key={index} delay={index * 0.1}>
              <div className="dark-card rounded-lg p-6 flex items-center space-x-4">
                {item.status === 'success' && <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0" />}
                {item.status === 'warning' && <AlertCircle className="h-6 w-6 text-yellow-500 flex-shrink-0" />}
                {item.status === 'error' && <XCircle className="h-6 w-6 text-cyan-400 flex-shrink-0" />}
                <div className="flex-1">
                  <p className="text-white font-bold">{item.message}</p>
                  <p className="text-zinc-500 text-sm">{item.time}</p>
                </div>
              </div>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </div>
  );
}
