'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AnalyticsRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/admin');
  }, [router]);

  return (
    <div className="h-full flex items-center justify-center bg-[#041618] text-[#80ADB0]">
      <div className="flex items-center gap-3">
        <span className="w-4 h-4 rounded-full border-2 border-[#FC6F01] border-t-transparent animate-spin" />
        <span className="text-sm font-semibold">Monitoring stantsiyasiga yo&apos;naltirilmoqda...</span>
      </div>
    </div>
  );
}
