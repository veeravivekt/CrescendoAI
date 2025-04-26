'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, X, GripVertical, Play } from 'lucide-react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

interface Track {
  id: string;
  title: string;
  artist: string;
  duration: string;
  coverUrl?: string;
}

interface QueueDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  queue: Track[];
  onQueueUpdate: (newQueue: Track[]) => void;
  onTrackSelect: (track: Track) => void;
  currentTrack?: Track;
}

export function QueueDrawer({
  isOpen,
  onClose,
  queue,
  onQueueUpdate,
  onTrackSelect,
  currentTrack
}: QueueDrawerProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;

    const items = Array.from(queue);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    onQueueUpdate(items);
    setIsDragging(false);
  };

  const handleDragStart = () => {
    setIsDragging(true);
  };

  const removeTrack = (index: number) => {
    const newQueue = [...queue];
    newQueue.splice(index, 1);
    onQueueUpdate(newQueue);
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

          {/* Drawer */}
          <motion.div
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ type: "spring", damping: 20 }}
            className="fixed left-0 top-0 h-full w-80 bg-white shadow-xl z-50"
          >
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b">
                <h2 className="text-lg font-semibold">Up Next</h2>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>

              {/* Queue List */}
              <div className="flex-1 overflow-y-auto p-4">
                <DragDropContext onDragEnd={handleDragEnd} onDragStart={handleDragStart}>
                  <Droppable droppableId="queue">
                    {(provided) => (
                      <div
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                        className="space-y-2"
                      >
                        {queue.map((track, index) => (
                          <Draggable
                            key={track.id}
                            draggableId={track.id}
                            index={index}
                          >
                            {(provided, snapshot) => (
                              <motion.div
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                className={`flex items-center gap-3 p-2 rounded-lg ${
                                  snapshot.isDragging ? 'bg-gray-100' : 'hover:bg-gray-50'
                                } ${
                                  currentTrack?.id === track.id ? 'bg-blue-50' : ''
                                }`}
                              >
                                <div
                                  {...provided.dragHandleProps}
                                  className="cursor-grab"
                                >
                                  <GripVertical className="w-5 h-5 text-gray-400" />
                                </div>

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
                                    onClick={() => onTrackSelect(track)}
                                    className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                                  >
                                    <Play className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => removeTrack(index)}
                                    className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                                  >
                                    <X className="w-4 h-4" />
                                  </button>
                                </div>
                              </motion.div>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                      </div>
                    )}
                  </Droppable>
                </DragDropContext>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
} 