'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Keyboard, MousePointer, Clock, RefreshCw } from 'lucide-react';

// Dummy data for demonstration
const dummyData = {
  keystroke: {
    speed: 3.2,
    errorRate: 2.1,
    trend: 'stable',
  },
  cursor: {
    jerkiness: 0.8,
    idleGaps: 45,
    scrollSpeed: 120,
    trend: 'improving',
  },
  engagement: {
    focusTime: 18,
    tabSwitches: 4,
    trend: 'declining',
  },
};

interface BehavioralInsightsProps {
  className?: string;
}

export function BehavioralInsights({ className }: BehavioralInsightsProps) {
  const [data, setData] = useState(dummyData);

  // Simulate data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => ({
        keystroke: {
          ...prev.keystroke,
          speed: +(Math.random() * 0.5 + 2.8).toFixed(1),
          errorRate: +(Math.random() * 0.5 + 1.8).toFixed(1),
        },
        cursor: {
          ...prev.cursor,
          jerkiness: +(Math.random() * 0.3 + 0.6).toFixed(1),
          idleGaps: Math.floor(Math.random() * 20 + 35),
          scrollSpeed: Math.floor(Math.random() * 30 + 100),
        },
        engagement: {
          ...prev.engagement,
          focusTime: Math.floor(Math.random() * 5 + 15),
          tabSwitches: Math.floor(Math.random() * 2 + 3),
        },
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
        return 'text-green-500';
      case 'declining':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return '↑';
      case 'declining':
        return '↓';
      default:
        return '→';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Behavioral Insights</h3>
        <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <RefreshCw className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Keystroke Dynamics */}
      <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
        <div className="flex items-center space-x-2 mb-3">
          <Keyboard className="w-5 h-5 text-blue-500" />
          <h4 className="font-medium text-gray-900">Keystroke Dynamics</h4>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-500 mb-1">Typing Speed</div>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-semibold">{data.keystroke.speed}</span>
              <span className="text-sm text-gray-500">chars/sec</span>
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Error Rate</div>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-semibold">{data.keystroke.errorRate}%</span>
              <span className={`text-sm ${getTrendColor(data.keystroke.trend)}`}>
                {getTrendIcon(data.keystroke.trend)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Cursor & Scroll Patterns */}
      <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
        <div className="flex items-center space-x-2 mb-3">
          <MousePointer className="w-5 h-5 text-purple-500" />
          <h4 className="font-medium text-gray-900">Cursor & Scroll Patterns</h4>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-500 mb-1">Smoothness</div>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-semibold">{data.cursor.jerkiness}</span>
              <span className={`text-sm ${getTrendColor(data.cursor.trend)}`}>
                {getTrendIcon(data.cursor.trend)}
              </span>
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Idle Gaps</div>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-semibold">{data.cursor.idleGaps}</span>
              <span className="text-sm text-gray-500">sec</span>
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Scroll Speed</div>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-semibold">{data.cursor.scrollSpeed}</span>
              <span className="text-sm text-gray-500">px/sec</span>
            </div>
          </div>
        </div>
      </div>

      {/* Screen Engagement */}
      <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
        <div className="flex items-center space-x-2 mb-3">
          <Clock className="w-5 h-5 text-green-500" />
          <h4 className="font-medium text-gray-900">Screen Engagement</h4>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-500 mb-1">Focus Time</div>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-semibold">{data.engagement.focusTime}</span>
              <span className="text-sm text-gray-500">min</span>
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500 mb-1">Tab Switches</div>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-semibold">{data.engagement.tabSwitches}</span>
              <span className="text-sm text-gray-500">/hr</span>
            </div>
          </div>
        </div>
      </div>

      {/* Info Tooltip */}
      <div className="text-sm text-gray-500">
        <p className="mb-2">These metrics help us understand your work patterns and provide better recommendations.</p>
        <p>All data is processed locally and never shared with third parties.</p>
      </div>
    </div>
  );
} 