'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Mood {
  id: string;
  name: string;
  icon: string;
  color: string;
  textColor: string;
  hoverColor: string;
  valence: number;
  arousal: number;
  description: string;
}

const MOODS: Mood[] = [
  {
    id: 'relaxed',
    name: 'Relaxed',
    icon: '🧘',
    color: '#A0DDE6',
    textColor: '#1F2937',
    hoverColor: '#7BC5D3',
    valence: 1,
    arousal: -1,
    description: 'Post-meditation, winding down, before sleep'
  },
  {
    id: 'content',
    name: 'Content',
    icon: '😊',
    color: '#8FD3A3',
    textColor: '#1F2937',
    hoverColor: '#6DB88A',
    valence: 1,
    arousal: 0,
    description: 'Light work, calm socializing'
  },
  {
    id: 'engaged',
    name: 'Engaged',
    icon: '⚡️',
    color: '#FCD34D',
    textColor: '#1F2937',
    hoverColor: '#FBBF24',
    valence: 1,
    arousal: 1,
    description: 'Deep flow state, creative bursts, energized focus'
  },
  {
    id: 'anxious',
    name: 'Anxious',
    icon: '😰',
    color: '#F2994A',
    textColor: '#1F2937',
    hoverColor: '#F27B0C',
    valence: -1,
    arousal: 1,
    description: 'Jitters, upcoming deadlines, mild panic'
  },
  {
    id: 'stressed',
    name: 'Stressed',
    icon: '🔥',
    color: '#E76F51',
    textColor: '#1F2937',
    hoverColor: '#D65D3B',
    valence: -1,
    arousal: 1,
    description: 'Overloaded, tight deadlines, cognitive overload'
  },
  {
    id: 'fatigued',
    name: 'Fatigued',
    icon: '😴',
    color: '#6C809A',
    textColor: '#1F2937',
    hoverColor: '#5A6B82',
    valence: 0,
    arousal: -1,
    description: 'Drained, post-lunch slump, end-of-day burnout'
  },
  {
    id: 'bored',
    name: 'Bored',
    icon: '😐',
    color: '#9CA3AF',
    textColor: '#1F2937',
    hoverColor: '#6B7280',
    valence: -1,
    arousal: 0,
    description: 'Monotonous tasks, mind-wandering'
  },
  {
    id: 'sad',
    name: 'Sad',
    icon: '😢',
    color: '#7D5BA6',
    textColor: '#FFFFFF',
    hoverColor: '#6B4B8E',
    valence: -1,
    arousal: -1,
    description: 'Low moments, introspection, grief'
  }
];

interface MoodWheelProps {
  onMoodSelect: (mood: Mood) => void;
  currentMood?: Mood;
}

export function MoodWheel({ onMoodSelect, currentMood }: MoodWheelProps) {
  const [selectedMood, setSelectedMood] = useState<Mood | null>(currentMood || null);

  const handleMoodSelect = (mood: Mood) => {
    setSelectedMood(mood);
    onMoodSelect(mood);
  };

  return (
    <div className="relative w-full max-w-md mx-auto">
      {/* Heading */}
      <div className="text-center mb-6">
        <motion.h2
          className="text-2xl font-bold text-gray-900"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          How are you feeling?
        </motion.h2>
        <motion.p
          className="text-gray-600 mt-2"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          Select your current mood to get personalized music recommendations
        </motion.p>
      </div>

      {/* Mood Grid */}
      <div className="grid grid-cols-4 gap-4 p-4">
        {MOODS.map((mood) => (
          <motion.button
            key={mood.id}
            className={`relative aspect-square rounded-xl flex flex-col items-center justify-center p-4 transition-all duration-200 ${
              selectedMood?.id === mood.id ? 'ring-2 ring-blue-500 ring-offset-2' : ''
            }`}
            style={{ 
              backgroundColor: mood.color,
              color: mood.textColor,
              border: '1px solid rgba(0, 0, 0, 0.1)'
            }}
            whileHover={{ 
              scale: 1.05,
              boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
            }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleMoodSelect(mood)}
          >
            <span className="text-3xl mb-2">{mood.icon}</span>
            <span className="text-sm font-medium">{mood.name}</span>
          </motion.button>
        ))}
      </div>

      {/* Selected Mood Display */}
      <AnimatePresence mode="wait">
        {selectedMood && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="mt-8 p-6 bg-white rounded-lg shadow-lg"
          >
            <div className="flex items-center space-x-4">
              <motion.div
                className="text-4xl"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 2 }}
              >
                {selectedMood.icon}
              </motion.div>
              <div>
                <motion.h3
                  className="text-xl font-semibold"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  {selectedMood.name}
                </motion.h3>
                <motion.p
                  className="text-gray-600"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  {selectedMood.description}
                </motion.p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
} 