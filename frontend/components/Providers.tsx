'use client';

import { ReactNode } from 'react';
import { RoleProvider } from '@/lib/useRole';

export default function Providers({ children }: { children: ReactNode }) {
  return <RoleProvider>{children}</RoleProvider>;
}
