'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

export type UserRole = 'citizen' | 'admin';

export interface UserSession {
  role: UserRole;
  citizenName?: string;
  citizenPhone?: string;
}

interface RoleContextType {
  session: UserSession;
  setRole: (role: UserRole) => void;
  setCitizenProfile: (name: string, phone: string) => void;
  logout: () => void;
  isReady: boolean;
  isRoleGateOpen: boolean;
  setIsRoleGateOpen: (open: boolean) => void;
  openRoleGate: () => void;
  closeRoleGate: () => void;
  hasSelectedRole: boolean;
}

const defaultSession: UserSession = {
  role: 'citizen',
  citizenName: 'Fuqaro',
  citizenPhone: '+998 (90) 123-45-67',
};

const RoleContext = createContext<RoleContextType>({
  session: defaultSession,
  setRole: () => {},
  setCitizenProfile: () => {},
  logout: () => {},
  isReady: false,
  isRoleGateOpen: false,
  setIsRoleGateOpen: () => {},
  openRoleGate: () => {},
  closeRoleGate: () => {},
  hasSelectedRole: false,
});

export function RoleProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<UserSession>(defaultSession);
  const [isReady, setIsReady] = useState(false);
  const [isRoleGateOpen, setIsRoleGateOpen] = useState(false);
  const [hasSelectedRole, setHasSelectedRole] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('sozlab_user_session') || localStorage.getItem('vazir_user_session');
      if (stored) {
        setSession(JSON.parse(stored));
      }
      const roleSelected = localStorage.getItem('sozlab_role_selected');
      if (!roleSelected) {
        setIsRoleGateOpen(true);
        setHasSelectedRole(false);
      } else {
        setHasSelectedRole(true);
      }
    } catch {
      // fallback to default
    } finally {
      setIsReady(true);
    }
  }, []);

  const saveSession = (newSession: UserSession) => {
    setSession(newSession);
    try {
      localStorage.setItem('sozlab_user_session', JSON.stringify(newSession));
    } catch {
      // ignore
    }
  };

  const setRole = (role: UserRole) => {
    const updated: UserSession = {
      ...session,
      role,
    };
    saveSession(updated);
    try {
      localStorage.setItem('sozlab_role_selected', 'true');
    } catch {
      // ignore
    }
    setHasSelectedRole(true);
    setIsRoleGateOpen(false);
  };

  const setCitizenProfile = (name: string, phone: string) => {
    const updated: UserSession = {
      ...session,
      citizenName: name,
      citizenPhone: phone,
    };
    saveSession(updated);
  };

  const logout = () => {
    try {
      localStorage.removeItem('sozlab_role_selected');
    } catch {
      // ignore
    }
    setHasSelectedRole(false);
    saveSession(defaultSession);
    setIsRoleGateOpen(true);
  };

  const openRoleGate = () => setIsRoleGateOpen(true);
  const closeRoleGate = () => setIsRoleGateOpen(false);

  return (
    <RoleContext.Provider
      value={{
        session,
        setRole,
        setCitizenProfile,
        logout,
        isReady,
        isRoleGateOpen,
        setIsRoleGateOpen,
        openRoleGate,
        closeRoleGate,
        hasSelectedRole,
      }}
    >
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  return useContext(RoleContext);
}
