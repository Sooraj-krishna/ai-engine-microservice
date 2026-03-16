import { AnimatedSection } from '@/components/shared/AnimatedSection';
import { Mail, Github, FileText, Send } from 'lucide-react';

export default function ContactPage() {
  return (
    <div className="page-enter min-h-screen py-24 px-4">
      {/* Hero Section */}
      <div className="relative mb-32">
        <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 opacity-5 pointer-events-none">
          <h1 className="text-[15vw] font-bold uppercase tracking-wider text-white text-center">
            CONTACT
          </h1>
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <AnimatedSection>
            <h1 className="text-5xl md:text-7xl font-bold uppercase tracking-wider text-white mb-6">
              Get in <span className="text-red-gradient">Touch</span>
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              Have questions? We're here to help
            </p>
          </AnimatedSection>
        </div>
      </div>

      {/* Contact Content */}
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <AnimatedSection delay={0.1}>
            <div className="dark-card rounded-lg p-8">
              <h2 className="text-2xl font-bold text-white uppercase tracking-wide mb-6">
                Send a Message
              </h2>

              <form className="space-y-6">
                <div>
                  <label className="block text-sm font-bold text-zinc-300 mb-2 uppercase tracking-wider">
                    Name
                  </label>
                  <input
                    type="text"
                    placeholder="Your name"
                    className="w-full px-4 py-3 bg-zinc-900 border border-zinc-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 placeholder:text-zinc-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-zinc-300 mb-2 uppercase tracking-wider">
                    Email
                  </label>
                  <input
                    type="email"
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 bg-zinc-900 border border-zinc-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 placeholder:text-zinc-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-zinc-300 mb-2 uppercase tracking-wider">
                    Subject
                  </label>
                  <input
                    type="text"
                    placeholder="How can we help?"
                    className="w-full px-4 py-3 bg-zinc-900 border border-zinc-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 placeholder:text-zinc-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-zinc-300 mb-2 uppercase tracking-wider">
                    Message
                  </label>
                  <textarea
                    rows={6}
                    placeholder="Your message..."
                    className="w-full px-4 py-3 bg-zinc-900 border border-zinc-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 placeholder:text-zinc-600 resize-none"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full inline-flex items-center justify-center space-x-2 px-8 py-4 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-red-600 hover:to-red-500 rounded-lg text-white font-bold uppercase tracking-wider transition-all shadow-lg shadow-cyan-950/50 hover:shadow-xl hover:shadow-cyan-900/50"
                >
                  <Send className="h-5 w-5" />
                  <span>Send Message</span>
                </button>
              </form>
            </div>
          </AnimatedSection>

          {/* Contact Information */}
          <AnimatedSection delay={0.2}>
            <div className="space-y-6">
              {/* Info Card */}
              <div className="dark-card rounded-lg p-8">
                <h2 className="text-2xl font-bold text-white uppercase tracking-wide mb-6">
                  Information
                </h2>

                <div className="space-y-6">
                  <a
                    href="https://github.com/your-repo/ai-engine-microservice"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-4 text-zinc-400 hover:text-cyan-400 transition-colors group"
                  >
                    <div className="w-12 h-12 bg-cyan-950/30 border border-cyan-800/50 rounded-lg flex items-center justify-center group-hover:border-cyan-700/70 transition-colors">
                      <Github className="h-6 w-6 text-cyan-400" />
                    </div>
                    <div>
                      <div className="text-sm text-zinc-500 uppercase tracking-wider">Repository</div>
                      <div className="font-bold text-white group-hover:text-cyan-400 transition-colors">
                        GitHub Repository
                      </div>
                    </div>
                  </a>

                  <a
                    href="mailto:support@aiengine.dev"
                    className="flex items-center space-x-4 text-zinc-400 hover:text-cyan-400 transition-colors group"
                  >
                    <div className="w-12 h-12 bg-cyan-950/30 border border-cyan-800/50 rounded-lg flex items-center justify-center group-hover:border-cyan-700/70 transition-colors">
                      <Mail className="h-6 w-6 text-cyan-400" />
                    </div>
                    <div>
                      <div className="text-sm text-zinc-500 uppercase tracking-wider">Email</div>
                      <div className="font-bold text-white group-hover:text-cyan-400 transition-colors">
                        support@aiengine.dev
                      </div>
                    </div>
                  </a>

                  <a
                    href="/docs"
                    className="flex items-center space-x-4 text-zinc-400 hover:text-cyan-400 transition-colors group"
                  >
                    <div className="w-12 h-12 bg-cyan-950/30 border border-cyan-800/50 rounded-lg flex items-center justify-center group-hover:border-cyan-700/70 transition-colors">
                      <FileText className="h-6 w-6 text-cyan-400" />
                    </div>
                    <div>
                      <div className="text-sm text-zinc-500 uppercase tracking-wider">Documentation</div>
                      <div className="font-bold text-white group-hover:text-cyan-400 transition-colors">
                        Read the Docs
                      </div>
                    </div>
                  </a>
                </div>
              </div>

              {/* CTA Card */}
              <div className="dark-card rounded-lg p-8 text-center">
                <h3 className="text-xl font-bold text-white mb-3 uppercase tracking-wide">
                  Ready to Start?
                </h3>
                <p className="text-zinc-400 mb-6">
                  Begin using AI Engine today
                </p>
                <a
                  href="/analysis"
                  className="inline-block px-8 py-3 bg-gradient-to-r from-cyan-600 to-teal-500 hover:from-red-600 hover:to-red-500 rounded-lg text-white font-bold uppercase tracking-wider transition-all shadow-lg shadow-cyan-950/50 hover:shadow-xl hover:shadow-cyan-900/50"
                >
                  Get Started
                </a>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </div>
    </div>
  );
}
