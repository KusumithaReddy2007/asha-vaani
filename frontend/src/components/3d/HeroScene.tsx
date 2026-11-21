import React from 'react';

export const HeroScene: React.FC = () => {
  return (
    <div className="w-full min-h-[580px] lg:min-h-[650px] flex items-center justify-center relative overflow-visible">
      <img
        src="/images/asha-worker-hero.png"
        alt="ASHA worker using the ASHA-VAANI voice assistant"
        className="block w-[130%] max-w-none h-auto object-contain"
        loading="eager"
      />
    </div>
  );
};
