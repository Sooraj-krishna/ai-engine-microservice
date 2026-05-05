import { AnimatedSection } from '@/components/shared/AnimatedSection';
import { Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function HistoryPage() {
  return (
    <div className="bg-black min-h-screen pt-28 pb-24 px-4 relative overflow-hidden">
      {/* Background ambient glows */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-white/[0.02] rounded-full blur-[150px] -ml-60 -mt-60 pointer-events-none" />

      <div className="max-w-4xl mx-auto relative z-10">
        {/* ── PAGE HEADER ─────────────────────────────── */}
        <AnimatedSection>
          <div className="text-center mb-20">
            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-600 mb-3">
              AI Engine · Archives
            </p>
            <h1 className="text-5xl md:text-7xl font-bold uppercase tracking-tighter text-white leading-none mb-4">
              Intelligence <span className="text-zinc-500 italic">History</span>
            </h1>
            <p className="text-base text-zinc-500 font-light max-w-xl mx-auto">
              Complete historical tracking of all autonomous analysis runs, anomalies detected, and authorized resolutions.
            </p>
          </div>
        </AnimatedSection>

        {/* ── MAIN CONTENT ────────────────────────────── */}
        <AnimatedSection delay={0.1}>
          <div className="premium-card p-12 text-center mb-12">
            <div className="w-20 h-20 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mx-auto mb-8">
              <Clock className="h-8 w-8 text-zinc-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-4 uppercase tracking-tighter">
              Archive Synchronization
            </h2>
            <p className="text-zinc-500 text-sm mb-10 max-w-md mx-auto leading-relaxed uppercase tracking-widest font-bold">
              Database synchronization in progress. Historical data visualization will be available in the next core update.
            </p>
            <a
              href="/analysis"
              className="inline-block px-10 py-4 bg-white text-black text-[10px] font-black uppercase tracking-[0.2em] rounded-full hover:bg-zinc-200 transition-all shadow-[0_0_30px_-5px_rgba(255,255,255,0.3)]"
            >
              Back to Live Intelligence
            </a>
          </div>
        </AnimatedSection>

        {/* ── TIMELINE PREVIEW ────────────────────────── */}
        <div className="space-y-4">
          <p className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-700 mb-6 text-center">Recent Activity Log</p>
          {[
            { status: 'success', time: '2 hours ago', message: 'Build validation passed successfully' },
            { status: 'warning', time: '5 hours ago', message: '3 anomalies detected and resolved' },
            { status: 'success', time: '1 day ago', message: 'Automated maintenance PR merged' },
          ].map((item, index) => (
            <AnimatedSection key={index} delay={0.2 + index * 0.1}>
              <div className="premium-card p-6 flex items-center space-x-5 hover:bg-white/[0.04] transition-colors group">
                <div className={`p-2.5 rounded-full ${
                  item.status === 'success' ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-amber-500/10 border border-amber-500/20'
                }`}>
                  {item.status === 'success' ? (
                    <CheckCircle className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-amber-400" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-bold text-white group-hover:text-zinc-300 transition-colors uppercase tracking-tight">{item.message}</p>
                  <p className="text-[9px] text-zinc-600 font-black uppercase tracking-widest mt-1">{item.time}</p>
                </div>
              </div>
            </AnimatedSection>
          ))}
        </div>
      </div>
    </div>
  );
}
