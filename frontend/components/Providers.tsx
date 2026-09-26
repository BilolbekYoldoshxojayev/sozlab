'use client';

import { ReactNode } from 'react';
import { RoleProvider } from '@/lib/useRole';
import { ThemeProvider } from '@/lib/useTheme';

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <RoleProvider>{children}</RoleProvider>
    </ThemeProvider>
  );
}
