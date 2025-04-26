'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Plus } from 'lucide-react';

interface Track {
  id: string;
  title: string;
  artist: string;
  duration: string;
  coverUrl?: string;
}

interface SearchBarProps {
  onAddToQueue: (track: Track) => void;
  onClose: () => void;
  isOpen: boolean;
}

export function SearchBar({ onAddToQueue, onClose, isOpen }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Track[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    } else {
      setQuery('');
      setResults([]);
    }
  }, [isOpen]);

  const handleSearch = async (value: string) => {
    setQuery(value);
    if (!value.trim()) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    try {
      // TODO: Replace with actual API call
      const mockResults: Track[] = [
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
      ];
      setResults(mockResults);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToQueue = (track: Track) => {
    onAddToQueue(track);
    setQuery('');
    setResults([]);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
          />

          {/* Search Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed top-20 left-1/2 -translate-x-1/2 bg-white rounded-lg w-full max-w-lg mx-4 shadow-xl z-50"
          >
            <div className="p-4 border-b">
              <div className="flex items-center gap-2">
                <Search className="w-5 h-5 text-gray-400" />
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => handleSearch(e.target.value)}
                  placeholder="Search for songs..."
                  className="flex-1 outline-none text-lg"
                />
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="max-h-[calc(100vh-12rem)] overflow-y-auto">
              <AnimatePresence>
                {isLoading ? (
                  <div className="p-4 text-center text-gray-500">
                    Searching...
                  </div>
                ) : results.length > 0 ? (
                  <div className="divide-y">
                    {results.map((track) => (
                      <motion.div
                        key={track.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="flex items-center gap-3 p-4 hover:bg-gray-50"
                      >
                        {track.coverUrl && (
                          <img
                            src={track.coverUrl}
                            alt={track.title}
                            className="w-12 h-12 rounded"
                          />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{track.title}</p>
                          <p className="text-sm text-gray-500 truncate">
                            {track.artist}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500">
                            {track.duration}
                          </span>
                          <button
                            onClick={() => handleAddToQueue(track)}
                            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                          >
                            <Plus className="w-5 h-5" />
                          </button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : query ? (
                  <div className="p-4 text-center text-gray-500">
                    No results found
                  </div>
                ) : null}
              </AnimatePresence>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
} 