import { Inter } from 'next/font/google';
import type { Metadata } from 'next';
import { TutorialOverlay } from '@/components/TutorialOverlay';
import { useState } from 'react';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'VibeFlow',
  description: 'AI-powered music that matches your mood',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
} 