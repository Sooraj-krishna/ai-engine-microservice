import { Cpu, Zap, Activity } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-gradient-to-r from-black via-zinc-950 to-black border-b-2 border-cyan-900/50 shadow-2xl shadow-cyan-950/20">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Cpu className="h-12 w-12 text-red-600 animate-pulse-glow" />
              <Zap className="h-5 w-5 text-cyan-400 absolute -top-1 -right-1" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white tracking-wider mb-1">
                AI ENGINE
              </h1>
              <p className="text-sm text-cyan-400 uppercase tracking-widest font-semibold">
                Self-Maintaining Microservice
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2 px-4 py-2 bg-zinc-900/50 border border-zinc-800 rounded-lg">
              <Activity className="h-4 w-4 text-cyan-400" />
              <span className="text-sm text-zinc-400 uppercase tracking-wider font-bold">v2.0.0</span>
            </div>
            <div className="status-badge online">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
              <span>Online</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
