'use client';

import { useState, useEffect } from 'react';
import { QueueDrawer } from '@/components/QueueDrawer';
import { SearchBar } from '@/components/SearchBar';
import { MoodWheel } from '@/components/MoodWheel';
import { NowPlayingCard } from '@/components/NowPlayingCard';
import { Player } from '@/components/Player';
import { SettingsDrawer } from '@/components/SettingsDrawer';
import { FeedbackRow } from '@/components/FeedbackRow';
import { Layout } from '@/components/Layout';
import { BreathingExercise } from '@/components/BreathingExercise';
import { Search, List } from 'lucide-react';

interface Track {
  id: string;
  title: string;
  artist: string;
  duration: string;
  coverUrl?: string;
}

export default function Home() {
  const [showBreathing, setShowBreathing] = useState(false);
  const [currentMood, setCurrentMood] = useState<any>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isQueueOpen, setIsQueueOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [queue, setQueue] = useState<Track[]>([
    {
      id: '1',
      title: 'Sample Track 1',
      artist: 'Artist 1',
      duration: '3:45',
      coverUrl: 'https://via.placeholder.com/48'
    },
    {
      id: '2',
      title: 'Sample Track 2',
      artist: 'Artist 2',
      duration: '4:20',
      coverUrl: 'https://via.placeholder.com/48'
    }
  ]);
  const [currentTrack, setCurrentTrack] = useState<Track | undefined>(queue[0]);

  // Monitor mood for breathing exercise
  useEffect(() => {
    if (currentMood?.id === 'anxious' || currentMood?.id === 'stressed') {
      setShowBreathing(true);
    }
  }, [currentMood]);

  const handleQueueUpdate = (newQueue: Track[]) => {
    setQueue(newQueue);
  };

  const handleTrackSelect = (track: Track) => {
    setCurrentTrack(track);
  };

  const handleAddToQueue = (track: Track) => {
    setQueue([...queue, track]);
    setIsSearchOpen(false);
  };

  const handleLike = () => {
    // TODO: Implement like functionality
    console.log('Liked track:', currentTrack?.title);
  };

  const handleDislike = () => {
    // TODO: Implement dislike functionality
    console.log('Disliked track:', currentTrack?.title);
  };

  const handleNeverPlay = () => {
    // TODO: Implement never play functionality
    console.log('Never play track:', currentTrack?.title);
    // Remove the track from the queue
    if (currentTrack) {
      const newQueue = queue.filter(track => track.id !== currentTrack.id);
      setQueue(newQueue);
      // If there are tracks left, play the next one
      if (newQueue.length > 0) {
        setCurrentTrack(newQueue[0]);
      } else {
        setCurrentTrack(undefined);
      }
    }
  };

  return (
    <Layout>
      <main className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-end h-16">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsSearchOpen(true)}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <Search className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setIsQueueOpen(true)}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <List className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column - Mood Selection */}
            <div>
              <MoodWheel
                onMoodSelect={(mood) => setCurrentMood(mood)}
              />
            </div>

            {/* Right Column - Music Player */}
            <div className="space-y-6">
              <NowPlayingCard track={currentTrack} />
              <Player
                track={currentTrack}
                onNext={() => {
                  const currentIndex = queue.findIndex(t => t.id === currentTrack?.id);
                  if (currentIndex < queue.length - 1) {
                    setCurrentTrack(queue[currentIndex + 1]);
                  }
                }}
                onPrevious={() => {
                  const currentIndex = queue.findIndex(t => t.id === currentTrack?.id);
                  if (currentIndex > 0) {
                    setCurrentTrack(queue[currentIndex - 1]);
                  }
                }}
              />
              <FeedbackRow
                onLike={handleLike}
                onDislike={handleDislike}
                onNeverPlay={handleNeverPlay}
              />
            </div>
          </div>
        </div>

        {/* Queue Drawer */}
        <QueueDrawer
          isOpen={isQueueOpen}
          onClose={() => setIsQueueOpen(false)}
          queue={queue}
          onQueueUpdate={handleQueueUpdate}
          onTrackSelect={handleTrackSelect}
          currentTrack={currentTrack}
        />

        {/* Search Bar */}
        <SearchBar
          isOpen={isSearchOpen}
          onAddToQueue={handleAddToQueue}
          onClose={() => setIsSearchOpen(false)}
        />
      </main>
      
      {/* Modals */}
      {showBreathing && (
        <BreathingExercise
          onComplete={() => setShowBreathing(false)}
          duration={30}
        />
      )}
    </Layout>
  );
} 