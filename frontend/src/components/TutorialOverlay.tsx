import React, { useState } from 'react';
import Joyride, { CallBackProps, STATUS, Step } from 'react-joyride';
import { tokens } from '@/lib/design-tokens';

interface TutorialOverlayProps {
  onComplete: () => void;
}

export const TutorialOverlay: React.FC<TutorialOverlayProps> = ({ onComplete }) => {
  const [run, setRun] = useState(true);

  const steps: Step[] = [
    {
      target: '.mood-gauge',
      content: 'This gauge shows your current mood state. It updates automatically based on your heart rate and movement.',
      placement: 'bottom',
      disableBeacon: true,
    },
    {
      target: '.manual-mood-selector',
      content: 'You can manually set your mood using these buttons if the automatic detection isn\'t accurate.',
      placement: 'top',
    },
    {
      target: '.now-playing-card',
      content: 'Here you can see what\'s currently playing, along with a tip about why this song was chosen for you.',
      placement: 'left',
    },
    {
      target: '.player-controls',
      content: 'Control playback with these buttons. The AI will adjust the music based on your mood and preferences.',
      placement: 'top',
    },
    {
      target: '.settings-drawer',
      content: 'Access settings to customize your experience, including energy levels and genre preferences.',
      placement: 'right',
    },
  ];

  const handleJoyrideCallback = (data: CallBackProps) => {
    const { status } = data;
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setRun(false);
      onComplete();
    }
  };

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showProgress
      showSkipButton
      styles={{
        options: {
          primaryColor: tokens.colors.primary,
          zIndex: 1000,
        },
        tooltipContainer: {
          textAlign: 'left',
        },
        buttonNext: {
          backgroundColor: tokens.colors.primary,
        },
        buttonBack: {
          marginRight: 10,
        },
      }}
      callback={handleJoyrideCallback}
      locale={{
        last: 'Finish',
        skip: 'Skip Tutorial',
      }}
    />
  );
}; 