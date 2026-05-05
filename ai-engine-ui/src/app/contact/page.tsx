import { AnimatedSection } from '@/components/shared/AnimatedSection';
import { Mail, Github, FileText, Send } from 'lucide-react';

export default function ContactPage() {
  return (
    <div className="bg-black min-h-screen pt-28 pb-24 px-4 relative overflow-hidden">
      {/* Background ambient glows */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-white/[0.02] rounded-full blur-[150px] -mr-60 -mt-60 pointer-events-none" />

      <div className="max-w-6xl mx-auto relative z-10">
        {/* ── PAGE HEADER ─────────────────────────────── */}
        <AnimatedSection>
          <div className="text-center mb-20">
            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-600 mb-3">
              AI Engine · Connectivity
            </p>
            <h1 className="text-5xl md:text-7xl font-bold uppercase tracking-tighter text-white leading-none mb-4">
              Get in <span className="text-zinc-500 italic">Touch</span>
            </h1>
            <p className="text-base text-zinc-500 font-light max-w-xl mx-auto">
              Heuristic feedback · Integration support · System inquiries
            </p>
          </div>
        </AnimatedSection>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <AnimatedSection delay={0.1}>
            <div className="premium-card p-10">
              <h2 className="text-xs font-black uppercase tracking-[0.3em] text-white mb-8 pb-4 border-b border-white/5">
                Terminal Message
              </h2>

              <form className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="block text-[9px] font-black text-zinc-600 mb-2 uppercase tracking-widest">
                      Identifier
                    </label>
                    <input
                      type="text"
                      placeholder="Name"
                      className="w-full px-5 py-3.5 bg-white/[0.02] border border-white/5 text-white rounded-2xl focus:outline-none focus:border-white/20 transition-all placeholder:text-zinc-700 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-[9px] font-black text-zinc-600 mb-2 uppercase tracking-widest">
                      Gateway
                    </label>
                    <input
                      type="email"
                      placeholder="Email"
                      className="w-full px-5 py-3.5 bg-white/[0.02] border border-white/5 text-white rounded-2xl focus:outline-none focus:border-white/20 transition-all placeholder:text-zinc-700 text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[9px] font-black text-zinc-600 mb-2 uppercase tracking-widest">
                    Subject
                  </label>
                  <input
                    type="text"
                    placeholder="Inquiry type"
                    className="w-full px-5 py-3.5 bg-white/[0.02] border border-white/5 text-white rounded-2xl focus:outline-none focus:border-white/20 transition-all placeholder:text-zinc-700 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-[9px] font-black text-zinc-600 mb-2 uppercase tracking-widest">
                    Payload
                  </label>
                  <textarea
                    rows={5}
                    placeholder="Describe your inquiry..."
                    className="w-full px-5 py-3.5 bg-white/[0.02] border border-white/5 text-white rounded-2xl focus:outline-none focus:border-white/20 transition-all placeholder:text-zinc-700 text-sm resize-none"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full flex items-center justify-center space-x-3 px-8 py-4 bg-white text-black text-[10px] font-black uppercase tracking-[0.2em] rounded-full hover:bg-zinc-200 transition-all shadow-[0_0_30px_-5px_rgba(255,255,255,0.2)]"
                >
                  <Send className="h-3.5 w-3.5" />
                  <span>Transmit Message</span>
                </button>
              </form>
            </div>
          </AnimatedSection>

          {/* Contact Information */}
          <AnimatedSection delay={0.2}>
            <div className="space-y-6">
              <div className="premium-card p-10">
                <h2 className="text-xs font-black uppercase tracking-[0.3em] text-white mb-10 pb-4 border-b border-white/5">
                  System Gateways
                </h2>

                <div className="space-y-8">
                  {[
                    { label: 'Repository', value: 'GitHub / AI-Engine', icon: <Github className="h-5 w-5" />, href: '#' },
                    { label: 'Intelligence Support', value: 'core@aiengine.dev', icon: <Mail className="h-5 w-5" />, href: 'mailto:core@aiengine.dev' },
                    { label: 'Documentation', value: 'System Heuristics', icon: <FileText className="h-5 w-5" />, href: '#' },
                  ].map((item, i) => (
                    <a
                      key={i}
                      href={item.href}
                      className="flex items-center space-x-5 text-zinc-400 hover:text-white transition-all group"
                    >
                      <div className="w-12 h-12 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-center group-hover:border-white/20 transition-all">
                        <span className="text-zinc-500 group-hover:text-white transition-colors">{item.icon}</span>
                      </div>
                      <div>
                        <div className="text-[9px] font-black text-zinc-600 uppercase tracking-widest mb-1">{item.label}</div>
                        <div className="text-sm font-bold text-white group-hover:text-zinc-300 transition-colors uppercase tracking-tight">
                          {item.value}
                        </div>
                      </div>
                    </a>
                  ))}
                </div>
              </div>

              <div className="premium-card p-10 text-center">
                <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white mb-3">
                  Autonomous Readiness
                </h3>
                <p className="text-zinc-500 text-[10px] mb-8 font-bold uppercase tracking-widest leading-relaxed">
                  Start your first intelligence cycle now
                </p>
                <a
                  href="/analysis"
                  className="inline-block px-10 py-4 bg-white/5 border border-white/10 hover:bg-white text-black hover:text-black rounded-full font-black uppercase tracking-widest text-[10px] transition-all"
                >
                  <span className="group-hover:text-black text-white">Initialize Analysis</span>
                </a>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </div>
    </div>
  );
}
