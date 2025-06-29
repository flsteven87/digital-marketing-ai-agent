import { MainLayout } from '@/components/layout/main-layout';
import { Hero } from '@/components/landing/Hero';
import { Features } from '@/components/landing/Features';

export default function Home() {
  return (
    <MainLayout>
      <Hero />
      <Features />
    </MainLayout>
  );
}