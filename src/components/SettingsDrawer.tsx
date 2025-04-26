import React, { useState } from 'react';
import { tokens } from '@/lib/design-tokens';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { Settings, X } from 'lucide-react';
import * as Dialog from '@radix-ui/react-dialog';
import * as Switch from '@radix-ui/react-switch';

interface SettingsDrawerProps {
  onEnergyChange: (value: number) => void;
  onGenreWeightChange: (genre: string, weight: number) => void;
  onExplorationToggle: (value: boolean) => void;
  onRefreshHistory: () => void;
  onResetData: () => void;
  className?: string;
}

export const SettingsDrawer: React.FC<SettingsDrawerProps> = ({
  onEnergyChange,
  onGenreWeightChange,
  onExplorationToggle,
  onRefreshHistory,
  onResetData,
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [energy, setEnergy] = useState(50);
  const [genreWeights, setGenreWeights] = useState({
    pop: 1,
    rock: 1,
    electronic: 1,
  });
  const [exploreNew, setExploreNew] = useState(true);

  const handleEnergyChange = (value: number) => {
    setEnergy(value);
    onEnergyChange(value);
  };

  const handleGenreWeightChange = (genre: string, weight: number) => {
    setGenreWeights(prev => ({ ...prev, [genre]: weight }));
    onGenreWeightChange(genre, weight);
  };

  const handleExplorationToggle = (value: boolean) => {
    setExploreNew(value);
    onExplorationToggle(value);
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={setIsOpen}>
      <Dialog.Trigger asChild>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className={cn('p-4 rounded-full bg-primary text-white', className)}
        >
          <Settings className="w-6 h-6" />
        </motion.button>
      </Dialog.Trigger>
      
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50" />
        <Dialog.Content className="fixed right-0 top-0 h-full w-80 bg-white p-6 shadow-lg">
          <div className="flex justify-between items-center mb-6">
            <Dialog.Title className="text-xl font-semibold">Settings</Dialog.Title>
            <Dialog.Close asChild>
              <button className="p-2 hover:bg-gray-100 rounded-full">
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                Energy Ceiling
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={energy}
                onChange={(e) => handleEnergyChange(Number(e.target.value))}
                className="w-full"
              />
              <div className="text-sm text-gray-500 mt-1">{energy}%</div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                Genre Preferences
              </label>
              {Object.entries(genreWeights).map(([genre, weight]) => (
                <div key={genre} className="mb-2">
                  <label className="block text-sm capitalize">{genre}</label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={weight}
                    onChange={(e) => handleGenreWeightChange(genre, Number(e.target.value))}
                    className="w-full"
                  />
                </div>
              ))}
            </div>
            
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">
                Explore New Music
              </label>
              <Switch.Root
                checked={exploreNew}
                onCheckedChange={handleExplorationToggle}
                className="w-11 h-6 bg-gray-200 rounded-full relative data-[state=checked]:bg-primary"
              >
                <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform data-[state=checked]:translate-x-5" />
              </Switch.Root>
            </div>
            
            <div className="space-y-2">
              <button
                onClick={onRefreshHistory}
                className="w-full py-2 px-4 bg-primary text-white rounded-md hover:bg-primary/90"
              >
                Refresh History
              </button>
              <button
                onClick={onResetData}
                className="w-full py-2 px-4 bg-danger text-white rounded-md hover:bg-danger/90"
              >
                Clear All Data
              </button>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}; 