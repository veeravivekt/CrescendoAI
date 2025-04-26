'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

interface BreathingExerciseProps {
  onComplete: () => void;
  duration?: number;
}

const BREATHING_PHASES = {
  inhale: { duration: 4000, scale: 1.5, color: 'bg-blue-100 text-blue-600' },
  hold: { duration: 4000, scale: 1.5, color: 'bg-green-100 text-green-600' },
  exhale: { duration: 4000, scale: 1, color: 'bg-purple-100 text-purple-600' },
  rest: { duration: 2000, scale: 1, color: 'bg-gray-100 text-gray-600' }
} as const;

type Phase = keyof typeof BREATHING_PHASES;

export function BreathingExercise({ onComplete, duration = 30 }: BreathingExerciseProps) {
  const [timeLeft, setTimeLeft] = useState(duration);
  const [phase, setPhase] = useState<Phase>('inhale');
  const [isActive, setIsActive] = useState(true);

  const handleComplete = useCallback(() => {
    setIsActive(false);
    onComplete();
  }, [onComplete]);

  // Timer for total exercise duration
  useEffect(() => {
    if (!isActive) return;

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          handleComplete();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isActive, handleComplete]);

  // Breathing cycle
  useEffect(() => {
    if (!isActive) return;

    let currentPhaseIndex = 0;
    const phases = Object.keys(BREATHING_PHASES) as Phase[];
    
    const cycle = setInterval(() => {
      currentPhaseIndex = (currentPhaseIndex + 1) % phases.length;
      setPhase(phases[currentPhaseIndex]);
    }, BREATHING_PHASES[phases[currentPhaseIndex]].duration);

    return () => clearInterval(cycle);
  }, [isActive]);

  const getPhaseText = () => {
    switch (phase) {
      case 'inhale':
        return 'Breathe In...';
      case 'hold':
        return 'Hold...';
      case 'exhale':
        return 'Breathe Out...';
      case 'rest':
        return 'Rest...';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div className="relative bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <button
          onClick={handleComplete}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
        >
          <X className="w-5 h-5 text-gray-600" />
        </button>

        <div className="text-center mb-8">
          <motion.h2
            className="text-2xl font-bold mb-2"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            Take a Breath
          </motion.h2>
          <p className="text-gray-600">Focus on your breathing for {duration} seconds</p>
        </div>

        <div className="flex flex-col items-center">
          <div className="relative w-48 h-48 mb-8">
            {/* Breathing Circle */}
            <motion.div
              animate={{ 
                scale: BREATHING_PHASES[phase].scale,
                backgroundColor: BREATHING_PHASES[phase].color.split(' ')[0]
              }}
              transition={{ 
                duration: BREATHING_PHASES[phase].duration / 1000,
                ease: "easeInOut"
              }}
              className="w-full h-full rounded-full flex items-center justify-center relative"
            >
              <motion.span
                className={`text-2xl font-semibold ${BREATHING_PHASES[phase].color.split(' ')[1]}`}
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {getPhaseText()}
              </motion.span>
            </motion.div>
          </div>

          <div className="text-center">
            <motion.p
              className="text-lg font-medium text-gray-700 mb-2"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {timeLeft} seconds remaining
            </motion.p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-blue-600 h-2 rounded-full"
                initial={{ width: '100%' }}
                animate={{ width: `${(timeLeft / duration) * 100}%` }}
                transition={{ duration: 1 }}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
} 