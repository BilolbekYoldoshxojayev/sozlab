import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';
import Providers from '@/components/Providers';

export const metadata: Metadata = {
  title: 'SözLab | Ta\'lim va Innovatsiyalar Vazirligi AI Qo\'ng\'iroq Markazi',
  description: 'SözLab — O\'zbekiston Respublikasi Oliy ta\'lim, fan va innovatsiyalar vazirligi uchun sun\'iy intellektga asoslangan ovozli va matnli qo\'ng\'iroq markazi.',
};


export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uz">
      <body className="min-h-screen flex flex-col bg-slate-50 font-sans antialiased">
        <Providers>
          <Navbar />
          <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
            {children}
          </main>
        </Providers>

        <footer className="bg-white border-t border-slate-200 py-6 mt-12 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div>
              © 2026 O&apos;zbekiston Respublikasi Oliy ta&apos;lim, fan va innovatsiyalar vazirligi. Barcha huquqlar himoyalangan.
            </div>
            <div className="flex items-center gap-4 text-slate-400">
              <span>Umummilliy AI Xakaton — Namangan</span>
              <span>•</span>
              <span className="text-emerald-600 font-semibold">Ta&apos;lim Treki</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
