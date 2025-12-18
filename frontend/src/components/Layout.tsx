import { ReactNode } from 'react';
import { Toolbar } from './Toolbar';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="flex flex-col h-screen bg-kolosal-950 text-white">
      <Toolbar />
      <main className="flex-1 overflow-hidden relative">
        {children}
      </main>
    </div>
  );
}
