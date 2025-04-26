'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, PieChart, Clock, TrendingUp, BarChart2 } from 'lucide-react';

// Dummy data for demonstration
const dummyMoodData = [
  { timestamp: Date.now() - 3600000, value: 75, label: 'calm' },
  { timestamp: Date.now() - 3000000, value: 60, label: 'focused' },
  { timestamp: Date.now() - 2400000, value: 85, label: 'energetic' },
  { timestamp: Date.now() - 1800000, value: 40, label: 'stressed' },
  { timestamp: Date.now() - 1200000, value: 65, label: 'calm' },
  { timestamp: Date.now() - 600000, value: 80, label: 'focused' },
  { timestamp: Date.now(), value: 70, label: 'energetic' },
];

interface MoodData {
  timestamp: number;
  value: number;
  label: string;
}

interface MoodHistoryProps {
  data?: MoodData[];
}

export function MoodHistory({ data = dummyMoodData }: MoodHistoryProps) {
  const [isSummaryOpen, setIsSummaryOpen] = useState(false);

  // Listen for clicks on the external button
  useEffect(() => {
    const handleClick = () => setIsSummaryOpen(true);
    const button = document.getElementById('mood-summary');
    if (button) {
      button.addEventListener('click', handleClick);
      return () => button.removeEventListener('click', handleClick);
    }
  }, []);

  // Calculate summary statistics
  const totalTime = data.length * 5; // Assuming 5-minute intervals
  const moodCounts = data.reduce((acc, curr) => {
    acc[curr.label] = (acc[curr.label] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const moodPercentages = Object.entries(moodCounts).map(([label, count]) => ({
    label,
    percentage: (count / data.length) * 100,
    minutes: count * 5,
  }));

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <BarChart2 className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold">Mood Analytics</h2>
        </div>
        <button
          id="mood-summary"
          className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <PieChart className="w-4 h-4 mr-2" />
          View Summary
        </button>
      </div>

      {/* Sparkline */}
      <div className="relative h-24 bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 mb-4">
        <div className="absolute inset-0 flex items-center">
          <svg
            className="w-full h-12"
            viewBox={`0 0 ${data.length * 10} 40`}
            preserveAspectRatio="none"
          >
            <path
              d={data
                .map(
                  (point, i) =>
                    `${i === 0 ? 'M' : 'L'} ${i * 10} ${
                      40 - (point.value / 100) * 40
                    }`
                )
                .join(' ')}
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="text-primary"
            />
          </svg>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {moodPercentages.slice(0, 3).map((mood) => (
          <div
            key={mood.label}
            className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 text-center"
          >
            <div className="text-sm text-gray-500 dark:text-gray-400 capitalize">
              {mood.label}
            </div>
            <div className="text-lg font-semibold">{mood.percentage.toFixed(0)}%</div>
          </div>
        ))}
      </div>

      {/* Summary Modal */}
      <AnimatePresence>
        {isSummaryOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 dark:bg-black/40 z-40"
              onClick={() => setIsSummaryOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white dark:bg-gray-800 rounded-lg shadow-xl z-50 p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Daily Mood Summary</h3>
                <button
                  onClick={() => setIsSummaryOpen(false)}
                  className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Pie Chart */}
              <div className="relative h-48 mb-4">
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  {moodPercentages.map((mood, index) => {
                    const startAngle = moodPercentages
                      .slice(0, index)
                      .reduce((acc, curr) => acc + (curr.percentage * 360) / 100, 0);
                    const endAngle = startAngle + (mood.percentage * 360) / 100;
                    const startRad = (startAngle * Math.PI) / 180;
                    const endRad = (endAngle * Math.PI) / 180;
                    const x1 = 50 + 40 * Math.cos(startRad);
                    const y1 = 50 + 40 * Math.sin(startRad);
                    const x2 = 50 + 40 * Math.cos(endRad);
                    const y2 = 50 + 40 * Math.sin(endRad);
                    const largeArcFlag = endAngle - startAngle > 180 ? 1 : 0;

                    return (
                      <path
                        key={mood.label}
                        d={`M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
                        fill={`hsl(${(index * 360) / moodPercentages.length}, 70%, 50%)`}
                      />
                    );
                  })}
                </svg>
              </div>

              {/* Stats */}
              <div className="space-y-2">
                {moodPercentages.map((mood) => (
                  <div
                    key={mood.label}
                    className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                  >
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{
                          backgroundColor: `hsl(${
                            (moodPercentages.findIndex((m) => m.label === mood.label) * 360) /
                            moodPercentages.length
                          }, 70%, 50%)`,
                        }}
                      />
                      <span className="capitalize">{mood.label}</span>
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {mood.minutes} minutes ({mood.percentage.toFixed(1)}%)
                    </div>
                  </div>
                ))}
              </div>

              {/* Total Time */}
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4" />
                    <span>Total Time</span>
                  </div>
                  <span className="font-medium">{totalTime} minutes</span>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
} 