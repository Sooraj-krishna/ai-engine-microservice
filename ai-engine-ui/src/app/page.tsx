import { Hero } from '@/components/home/Hero';
import { FeaturesShowcase } from '@/components/home/FeaturesShowcase';
import { CTASection } from '@/components/home/CTASection';

export default function Home() {
  return (
    <div className="page-enter">
      <Hero />
      <FeaturesShowcase />
      <CTASection />
    </div>
  );
}
