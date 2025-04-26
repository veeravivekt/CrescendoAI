'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ThumbsUp, ThumbsDown, X, RotateCcw } from 'lucide-react';

interface FeedbackRowProps {
  onLike: () => void;
  onDislike: () => void;
  onNeverPlay: () => void;
}

export function FeedbackRow({ onLike, onDislike, onNeverPlay }: FeedbackRowProps) {
  const [showUndo, setShowUndo] = useState(false);
  const [lastAction, setLastAction] = useState<'like' | 'dislike' | 'never' | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleAction = (action: 'like' | 'dislike' | 'never') => {
    if (isAnimating) return;
    setIsAnimating(true);
    setLastAction(action);
    setShowUndo(true);

    switch (action) {
      case 'like':
        onLike();
        break;
      case 'dislike':
        onDislike();
        break;
      case 'never':
        onNeverPlay();
        break;
    }

    // Hide undo button after 3 seconds
    setTimeout(() => {
      setShowUndo(false);
      setIsAnimating(false);
    }, 3000);
  };

  const handleUndo = () => {
    setShowUndo(false);
    setLastAction(null);
  };

  const buttonVariants = {
    initial: { scale: 1 },
    hover: { scale: 1.1 },
    tap: { scale: 0.9 },
    animate: { scale: 1 }
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="flex space-x-6">
        <motion.button
          variants={buttonVariants}
          initial="initial"
          whileHover="hover"
          whileTap="tap"
          animate="animate"
          onClick={() => handleAction('like')}
          className="p-4 rounded-full bg-gradient-to-br from-green-400 to-green-600 text-white shadow-lg hover:shadow-xl transition-all duration-300"
          disabled={isAnimating}
        >
          <ThumbsUp className="w-6 h-6" />
        </motion.button>

        <motion.button
          variants={buttonVariants}
          initial="initial"
          whileHover="hover"
          whileTap="tap"
          animate="animate"
          onClick={() => handleAction('dislike')}
          className="p-4 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 text-white shadow-lg hover:shadow-xl transition-all duration-300"
          disabled={isAnimating}
        >
          <ThumbsDown className="w-6 h-6" />
        </motion.button>

        <motion.button
          variants={buttonVariants}
          initial="initial"
          whileHover="hover"
          whileTap="tap"
          animate="animate"
          onClick={() => handleAction('never')}
          className="p-4 rounded-full bg-gradient-to-br from-red-400 to-red-600 text-white shadow-lg hover:shadow-xl transition-all duration-300"
          disabled={isAnimating}
        >
          <X className="w-6 h-6" />
        </motion.button>
      </div>

      <AnimatePresence>
        {showUndo && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="flex items-center space-x-3 bg-white rounded-full px-4 py-2 shadow-lg"
          >
            <span className="text-sm font-medium text-gray-700">
              {lastAction === 'like' && 'Liked'}
              {lastAction === 'dislike' && 'Disliked'}
              {lastAction === 'never' && 'Never Play'}
            </span>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleUndo}
              className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Undo</span>
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
} 