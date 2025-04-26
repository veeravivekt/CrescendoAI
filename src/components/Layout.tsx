'use client';

import { ReactNode, useState } from 'react';
import { Settings, Home, BarChart2, PieChart, X } from 'lucide-react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { BehavioralInsights } from './BehavioralInsights';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isSummaryOpen, setIsSummaryOpen] = useState(false);
  const [selectedSetting, setSelectedSetting] = useState('account');

  const settingsContent = {
    account: (
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900">Account Settings</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Email</span>
            <span className="text-sm font-medium">user@example.com</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Password</span>
            <button className="text-sm text-blue-600 hover:text-blue-700">Change</button>
          </div>
        </div>
      </div>
    ),
    preferences: (
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900">Preferences</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Theme</span>
            <select className="text-sm border rounded px-2 py-1">
              <option>Light</option>
              <option>Dark</option>
              <option>System</option>
            </select>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Language</span>
            <select className="text-sm border rounded px-2 py-1">
              <option>English</option>
              <option>Spanish</option>
              <option>French</option>
            </select>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Music Quality</span>
            <select className="text-sm border rounded px-2 py-1">
              <option>High</option>
              <option>Medium</option>
              <option>Low</option>
            </select>
          </div>
        </div>
      </div>
    ),
    notifications: (
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900">Notifications</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Email Notifications</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Push Notifications</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Weekly Summary</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>
    ),
    help: (
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900">Help & Support</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">FAQ</span>
            <button className="text-sm text-blue-600 hover:text-blue-700">View</button>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Contact Support</span>
            <span className="text-sm font-medium">support@vibeflow.com</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Community Forum</span>
            <button className="text-sm text-blue-600 hover:text-blue-700">Join</button>
          </div>
        </div>
      </div>
    ),
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Fixed Header */}
      <header className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md border-b border-gray-200 z-50">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2 group">
            <motion.span 
              className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              VibeFlow
            </motion.span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              aria-label="Home"
            >
              <Home className="w-5 h-5 text-gray-600" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setIsHistoryOpen(true)}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              aria-label="History"
            >
              <BarChart2 className="w-5 h-5 text-gray-600" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setIsSummaryOpen(true)}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              aria-label="Summary"
            >
              <PieChart className="w-5 h-5 text-gray-600" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setIsSettingsOpen(!isSettingsOpen)}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              aria-label="Settings"
            >
              <Settings className="w-5 h-5 text-gray-600" />
            </motion.button>
          </nav>
        </div>
      </header>

      {/* Settings Drawer */}
      <AnimatePresence>
        {isSettingsOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-16 right-4 bg-white rounded-lg shadow-lg p-0 w-[640px] z-50 flex"
          >
            {/* Sidebar */}
            <div className="w-56 border-r p-6 bg-gray-50">
              <h3 className="font-semibold text-gray-900 mb-6">Settings</h3>
              <div className="space-y-1">
                <button
                  onClick={() => setSelectedSetting('account')}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    selectedSetting === 'account'
                      ? 'bg-white text-blue-700 font-medium shadow-sm'
                      : 'hover:bg-white/50'
                  }`}
                >
                  Account Settings
                </button>
                <button
                  onClick={() => setSelectedSetting('preferences')}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    selectedSetting === 'preferences'
                      ? 'bg-white text-blue-700 font-medium shadow-sm'
                      : 'hover:bg-white/50'
                  }`}
                >
                  Preferences
                </button>
                <button
                  onClick={() => setSelectedSetting('notifications')}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    selectedSetting === 'notifications'
                      ? 'bg-white text-blue-700 font-medium shadow-sm'
                      : 'hover:bg-white/50'
                  }`}
                >
                  Notifications
                </button>
                <button
                  onClick={() => setSelectedSetting('behavioral')}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    selectedSetting === 'behavioral'
                      ? 'bg-white text-blue-700 font-medium shadow-sm'
                      : 'hover:bg-white/50'
                  }`}
                >
                  Behavioral Insights
                </button>
                <button
                  onClick={() => setSelectedSetting('help')}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    selectedSetting === 'help'
                      ? 'bg-white text-blue-700 font-medium shadow-sm'
                      : 'hover:bg-white/50'
                  }`}
                >
                  Help & Support
                </button>
              </div>
            </div>
            {/* Content */}
            <div className="flex-1 p-8 relative">
              <button
                onClick={() => setIsSettingsOpen(false)}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
              <div className="max-w-[480px]">
                {selectedSetting === 'behavioral' ? (
                  <BehavioralInsights />
                ) : (
                  settingsContent[selectedSetting as keyof typeof settingsContent]
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* History Drawer */}
      <AnimatePresence>
        {isHistoryOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-16 right-4 bg-white rounded-lg shadow-lg p-4 w-80 z-50"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Mood History</h3>
                <button
                  onClick={() => setIsHistoryOpen(false)}
                  className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="space-y-4">
                {/* Today's History */}
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Today</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        <span className="text-sm">Calm</span>
                      </div>
                      <span className="text-xs text-gray-500">2 hours ago</span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 rounded-full bg-yellow-500" />
                        <span className="text-sm">Focused</span>
                      </div>
                      <span className="text-xs text-gray-500">1 hour ago</span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 rounded-full bg-blue-500" />
                        <span className="text-sm">Energetic</span>
                      </div>
                      <span className="text-xs text-gray-500">30 mins ago</span>
                    </div>
                  </div>
                </div>

                {/* Yesterday's History */}
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Yesterday</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 rounded-full bg-red-500" />
                        <span className="text-sm">Stressed</span>
                      </div>
                      <span className="text-xs text-gray-500">5 hours ago</span>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 rounded-full bg-purple-500" />
                        <span className="text-sm">Relaxed</span>
                      </div>
                      <span className="text-xs text-gray-500">3 hours ago</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Summary Drawer */}
      <AnimatePresence>
        {isSummaryOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-16 right-4 bg-white rounded-lg shadow-lg p-4 w-80 z-50"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Mood Summary</h3>
                <button
                  onClick={() => setIsSummaryOpen(false)}
                  className="p-1 rounded-full hover:bg-gray-100 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="space-y-4">
                {/* Mood Distribution */}
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Mood Distribution</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                        <span className="text-sm">Calm</span>
                      </div>
                      <span className="text-sm font-medium">40%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 rounded-full bg-yellow-500" />
                        <span className="text-sm">Focused</span>
                      </div>
                      <span className="text-sm font-medium">30%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 rounded-full bg-blue-500" />
                        <span className="text-sm">Energetic</span>
                      </div>
                      <span className="text-sm font-medium">20%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 rounded-full bg-red-500" />
                        <span className="text-sm">Stressed</span>
                      </div>
                      <span className="text-sm font-medium">10%</span>
                    </div>
                  </div>
                </div>

                {/* Quick Stats */}
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Quick Stats</h4>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-2 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-500">Total Entries</div>
                      <div className="text-lg font-semibold">24</div>
                    </div>
                    <div className="p-2 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-500">Most Common</div>
                      <div className="text-lg font-semibold">Calm</div>
                    </div>
                    <div className="p-2 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-500">Average Duration</div>
                      <div className="text-lg font-semibold">2.5h</div>
                    </div>
                    <div className="p-2 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-500">Last Updated</div>
                      <div className="text-lg font-semibold">30m ago</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="pt-16">
        {children}
      </main>
    </div>
  );
} 