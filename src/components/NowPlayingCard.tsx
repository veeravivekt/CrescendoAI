'use client';

import { motion } from 'framer-motion';
import { Music } from 'lucide-react';

interface Track {
  id: string;
  title: string;
  artist: string;
  duration: string;
  coverUrl?: string;
}

interface NowPlayingCardProps {
  track?: Track;
}

export function NowPlayingCard({ track }: NowPlayingCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-4">
        {/* Album Art */}
        <div className="relative w-24 h-24 rounded-lg overflow-hidden bg-gray-100">
          {track?.coverUrl ? (
            <img
              src={track.coverUrl}
              alt={track.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Music className="w-8 h-8 text-gray-400" />
            </div>
          )}
          <motion.div
            className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          />
        </div>

        {/* Track Info */}
        <div className="flex-1 min-w-0">
          <motion.h3
            className="text-lg font-semibold truncate"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {track?.title || 'No track selected'}
          </motion.h3>
          <motion.p
            className="text-gray-500 truncate"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            {track?.artist || 'Unknown artist'}
          </motion.p>
          <motion.p
            className="text-sm text-gray-400 mt-1"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            {track?.duration || '0:00'}
          </motion.p>
        </div>
      </div>

      {/* Mood Match Indicator */}
      {track && (
        <motion.div
          className="mt-4 p-3 bg-blue-50 rounded-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <p className="text-sm text-blue-600">
            This track matches your current mood
          </p>
        </motion.div>
      )}
    </div>
  );
} 