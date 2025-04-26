'use client';

import { useState, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, BarChart2 } from 'lucide-react';
import { FeedbackRow } from '@/components/FeedbackRow';
import { MoodHistory } from '@/components/MoodHistory';
import { useVibeFlow } from '@/hooks/useVibeFlow';

export default function Home() {
  const [isPlaying, setIsPlaying] = useState(false);
  const { moodHistory, addMood } = useVibeFlow();

  // Simulate mood changes every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      const moods = ['calm', 'focused', 'energetic', 'stressed'];
      const randomMood = moods[Math.floor(Math.random() * moods.length)];
      addMood({
        value: Math.random() * 100,
        label: randomMood,
      });
    }, 5000); // 5 seconds for demo purposes

    return () => clearInterval(interval);
  }, [addMood]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Now Playing Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Now Playing</h2>
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            <div className="flex-1">
              <h3 className="font-medium">Song Title</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Artist Name</p>
            </div>
            <div className="flex items-center space-x-2">
              <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
                <SkipBack className="w-5 h-5" />
              </button>
              <button 
                className="p-3 rounded-full bg-primary text-white hover:bg-primary-600"
                onClick={() => setIsPlaying(!isPlaying)}
              >
                {isPlaying ? (
                  <Pause className="w-6 h-6" />
                ) : (
                  <Play className="w-6 h-6" />
                )}
              </button>
              <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
                <SkipForward className="w-5 h-5" />
              </button>
              <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
                <Volume2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Mood Analytics Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <BarChart2 className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold">Mood Analytics</h2>
            </div>
            <button
              onClick={() => document.getElementById('mood-summary')?.click()}
              className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-600 transition-colors"
            >
              <BarChart2 className="w-4 h-4 mr-2" />
              View Mood Summary
            </button>
          </div>
          <MoodHistory data={moodHistory} />
        </div>

        {/* Feedback Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4">How's your vibe?</h2>
          <FeedbackRow
            onLike={() => console.log('Liked')}
            onDislike={() => console.log('Disliked')}
            onNeverPlay={() => console.log('Never play')}
            onSkip={() => console.log('Skipped')}
          />
        </div>
      </div>
    </div>
  );
}
