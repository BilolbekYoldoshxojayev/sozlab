'use client';

import React, { createContext, useContext, ReactNode } from 'react';

export type AppTheme = 'sozlab-unified';

interface ThemeContextType {
  theme: AppTheme;
  setTheme: (theme: AppTheme) => void;
  cycleTheme: () => void;
  themeConfig: {
    id: AppTheme;
    label: string;
    description: string;
  };
}

const THEME_CONFIG = {
  id: 'sozlab-unified' as AppTheme,
  label: "SözLab Yagona Davlat Uslubi",
  description: "Qora, To'q Ko'k va Oq ranglar tizimi"
};

const ThemeContext = createContext<ThemeContextType>({
  theme: 'sozlab-unified',
  setTheme: () => {},
  cycleTheme: () => {},
  themeConfig: THEME_CONFIG,
});

export function ThemeProvider({ children }: { children: ReactNode }) {
  return (
    <ThemeContext.Provider
      value={{
        theme: 'sozlab-unified',
        setTheme: () => {},
        cycleTheme: () => {},
        themeConfig: THEME_CONFIG,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
