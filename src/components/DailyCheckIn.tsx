'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MoodWheel } from './MoodWheel';
import { Slider } from '@/components/ui/slider';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

interface DailyCheckInProps {
  onComplete: (data: CheckInData) => void;
  onClose: () => void;
}

interface CheckInData {
  mood: string;
  stressLevel: number;
  note: string;
}

export function DailyCheckIn({ onComplete, onClose }: DailyCheckInProps) {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<CheckInData>({
    mood: '',
    stressLevel: 3,
    note: ''
  });

  const handleMoodSelect = (mood: any) => {
    setData(prev => ({ ...prev, mood: mood.id }));
    setStep(2);
  };

  const handleStressChange = (value: number[]) => {
    setData(prev => ({ ...prev, stressLevel: value[0] }));
  };

  const handleNoteChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setData(prev => ({ ...prev, note: e.target.value }));
  };

  const handleSubmit = () => {
    onComplete(data);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
      >
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold mb-2">Daily Check-In</h2>
          <p className="text-gray-600">Take a moment to reflect on how you're feeling</p>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="mood"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <h3 className="text-lg font-semibold mb-4">How are you feeling right now?</h3>
              <div className="relative">
                <MoodWheel onMoodSelect={handleMoodSelect} />
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="stress"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <h3 className="text-lg font-semibold mb-4">Rate your stress level (1-5)</h3>
              <div className="px-4">
                <Slider
                  value={[data.stressLevel]}
                  onValueChange={handleStressChange}
                  min={1}
                  max={5}
                  step={1}
                  className="mb-4"
                />
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Calm</span>
                  <span>Stressed</span>
                </div>
              </div>
              <div className="flex justify-between mt-6">
                <Button variant="outline" onClick={() => setStep(1)}>Back</Button>
                <Button onClick={() => setStep(3)}>Next</Button>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="note"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-4"
            >
              <h3 className="text-lg font-semibold mb-4">Any quick note? (optional)</h3>
              <Textarea
                value={data.note}
                onChange={handleNoteChange}
                placeholder="Share your thoughts..."
                className="mb-6"
              />
              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setStep(2)}>Back</Button>
                <Button onClick={handleSubmit}>Complete</Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
} 