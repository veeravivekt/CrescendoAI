import React from 'react';
import { tokens } from '@/lib/design-tokens';
import { cn } from '@/lib/utils';

interface MoodGaugeProps {
  mood: 'calm' | 'neutral' | 'stressed';
  className?: string;
}

export const MoodGauge: React.FC<MoodGaugeProps> = ({ mood, className }) => {
  const moodPositions = {
    calm: 0,
    neutral: 120,
    stressed: 240,
  };

  return (
    <div className={cn('relative w-64 h-64', className)}>
      <svg
        viewBox="0 0 100 100"
        className="w-full h-full"
      >
        {/* Background circle */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="5"
        />
        
        {/* Mood segments */}
        <path
          d="M50 5 A45 45 0 0 1 95 50"
          fill="none"
          stroke={tokens.colors.calm}
          strokeWidth="5"
        />
        <path
          d="M95 50 A45 45 0 0 1 50 95"
          fill="none"
          stroke={tokens.colors.neutral}
          strokeWidth="5"
        />
        <path
          d="M50 95 A45 45 0 0 1 5 50"
          fill="none"
          stroke={tokens.colors.stressed}
          strokeWidth="5"
        />
        
        {/* Needle */}
        <line
          x1="50"
          y1="50"
          x2="50"
          y2="10"
          stroke="#1f2937"
          strokeWidth="2"
          transform={`rotate(${moodPositions[mood]}, 50, 50)`}
        />
      </svg>
      
      {/* Mood text */}
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-lg font-medium capitalize">{mood}</span>
      </div>
    </div>
  );
}; 