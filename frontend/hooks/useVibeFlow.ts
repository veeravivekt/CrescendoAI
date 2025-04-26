import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  email: string;
  favorites: string[];
  history: string[];
}

interface MoodData {
  timestamp: number;
  value: number;
  label: string;
}

interface VibeFlowState {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
  addToFavorites: (songId: string) => void;
  removeFromFavorites: (songId: string) => void;
  addToHistory: (songId: string) => void;
  clearHistory: () => void;
  moodHistory: MoodData[];
  addMood: (mood: Omit<MoodData, 'timestamp'>) => void;
  clearMoodHistory: () => void;
}

export const useVibeFlow = create<VibeFlowState>()(
  persist(
    (set) => ({
      user: null,
      setUser: (user) => set({ user }),
      logout: () => set({ user: null }),
      addToFavorites: (songId) =>
        set((state) => ({
          user: state.user
            ? {
                ...state.user,
                favorites: [...(state.user.favorites || []), songId],
              }
            : null,
        })),
      removeFromFavorites: (songId) =>
        set((state) => ({
          user: state.user
            ? {
                ...state.user,
                favorites: (state.user.favorites || []).filter((id) => id !== songId),
              }
            : null,
        })),
      addToHistory: (songId) =>
        set((state) => ({
          user: state.user
            ? {
                ...state.user,
                history: [songId, ...(state.user.history || [])].slice(0, 50),
              }
            : null,
        })),
      clearHistory: () =>
        set((state) => ({
          user: state.user
            ? {
                ...state.user,
                history: [],
              }
            : null,
        })),
      moodHistory: [],
      addMood: (mood) =>
        set((state) => ({
          moodHistory: [
            { ...mood, timestamp: Date.now() },
            ...state.moodHistory,
          ].slice(0, 100), // Keep last 100 mood entries
        })),
      clearMoodHistory: () => set({ moodHistory: [] }),
    }),
    {
      name: 'vibeflow-storage',
      skipHydration: true,
    }
  )
); 