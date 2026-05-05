import EtherealBeamsHero from "@/components/ui/ethereal-beams-hero";
import { FeaturesShowcase } from '@/components/home/FeaturesShowcase';
import { CTASection } from '@/components/home/CTASection';

export default function Home() {
  return (
    <div className="bg-black min-h-screen pb-32">
      <EtherealBeamsHero />
      
      <div className="relative z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black to-black pointer-events-none h-64" />
        <FeaturesShowcase />
        <CTASection />
      </div>

      {/* Footer Branding */}
      <footer className="py-20 px-4 border-t border-white/5 text-center">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center space-x-2 mb-8">
            <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
              <span className="text-black font-black text-[8px]">AI</span>
            </div>
            <span className="text-white font-black tracking-[0.3em] text-xs">
              AI ENGINE CORE
            </span>
          </div>
          <p className="text-zinc-600 text-[10px] uppercase tracking-widest font-medium">
            © 2026 Autonomous Engineering Systems. All Rights Reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
