import React, { useState } from 'react';
import { tokens } from '@/lib/design-tokens';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { Smile, Meh, Frown } from 'lucide-react';

interface ManualMoodSelectorProps {
  onMoodSelect: (mood: 'calm' | 'neutral' | 'stressed') => void;
  className?: string;
}

export const ManualMoodSelector: React.FC<ManualMoodSelectorProps> = ({
  onMoodSelect,
  className,
}) => {
  const [selectedMood, setSelectedMood] = useState<'calm' | 'neutral' | 'stressed' | null>(null);
  const [showUndo, setShowUndo] = useState(false);

  const handleMoodSelect = (mood: 'calm' | 'neutral' | 'stressed') => {
    setSelectedMood(mood);
    onMoodSelect(mood);
    setShowUndo(true);
    setTimeout(() => setShowUndo(false), 5000);
  };

  const handleUndo = () => {
    setSelectedMood(null);
    setShowUndo(false);
  };

  const moodButtons = [
    { mood: 'calm' as const, icon: Smile, color: tokens.colors.calm },
    { mood: 'neutral' as const, icon: Meh, color: tokens.colors.neutral },
    { mood: 'stressed' as const, icon: Frown, color: tokens.colors.stressed },
  ];

  return (
    <div className={cn('flex flex-col items-center gap-4', className)}>
      <div className="flex gap-4">
        {moodButtons.map(({ mood, icon: Icon, color }) => (
          <motion.button
            key={mood}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={cn(
              'p-4 rounded-full',
              selectedMood === mood ? 'ring-2 ring-offset-2' : 'hover:ring-2 hover:ring-offset-2',
              `ring-${color}`
            )}
            onClick={() => handleMoodSelect(mood)}
          >
            <Icon className="w-8 h-8" style={{ color }} />
          </motion.button>
        ))}
      </div>

      {showUndo && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white shadow-lg rounded-lg p-4"
        >
          <p className="text-sm">
            Selected mood: <span className="font-medium capitalize">{selectedMood}</span>
          </p>
          <button
            className="text-sm text-primary hover:underline mt-2"
            onClick={handleUndo}
          >
            Undo
          </button>
        </motion.div>
      )}
    </div>
  );
}; 