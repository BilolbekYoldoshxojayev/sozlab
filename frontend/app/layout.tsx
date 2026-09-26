import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';
import Providers from '@/components/Providers';

export const metadata: Metadata = {
  title: "SözLab | Oliy Ta'lim, Fan va Innovatsiyalar Vazirligi AI Call-Markazi",
  description: "SözLab — O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi hamda Maktabgacha va maktab ta'limi vazirligi uchun 100% avtonom sun'iy intellektli ovozli call-markaz.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uz" data-theme="dark-blue">
      <body
        className="h-screen w-screen overflow-hidden flex flex-col font-sans antialiased bg-slate-50 text-slate-900 select-none"
      >
        <Providers>
          <Navbar />
          <main className="flex-1 w-full overflow-hidden flex flex-col">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
