import React, { useEffect, useRef } from 'react';

interface WaveformVisualizerProps {
  analyser?: AnalyserNode | null;
  isActive: boolean;
  barCount?: number;
}

export const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  analyser,
  isActive,
  barCount = 48,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    const dataArray = analyser ? new Uint8Array(analyser.frequencyBinCount) : new Uint8Array(barCount);

    const render = () => {
      animationId = requestAnimationFrame(render);
      const width = canvas.width;
      const height = canvas.height;

      ctx.clearRect(0, 0, width, height);

      if (analyser && isActive) {
        analyser.getByteFrequencyData(dataArray);
      }

      const barWidth = (width / barCount) * 0.75;
      const gap = (width / barCount) * 0.25;

      for (let i = 0; i < barCount; i++) {
        let value = 0;
        if (analyser && isActive) {
          const index = Math.floor((i / barCount) * dataArray.length * 0.6);
          value = dataArray[index] / 255.0;
        } else if (isActive) {
          // Synthetic ambient wave if listening without active mic node
          value = 0.25 + 0.35 * Math.sin(Date.now() * 0.006 + i * 0.28);
        } else {
          // Idle low shimmer
          value = 0.05 + 0.03 * Math.sin(Date.now() * 0.002 + i * 0.15);
        }

        const barHeight = Math.max(value * height * 0.88, 4);
        const x = i * (barWidth + gap);
        const y = (height - barHeight) / 2;

        // Gradient coloring from neon turquoise to deep teal
        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, '#00f5d4');
        gradient.addColorStop(0.5, '#14b8a6');
        gradient.addColorStop(1, '#0d9488');

        ctx.fillStyle = gradient;
        ctx.shadowBlur = isActive ? 12 : 2;
        ctx.shadowColor = '#00f5d4';

        // Rounded bar
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, 3);
        ctx.fill();
      }
    };

    render();

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [analyser, isActive, barCount]);

  return (
    <canvas
      ref={canvasRef}
      width={480}
      height={72}
      className="w-full h-16 rounded-xl bg-emerald-950/40 border border-teal-500/20 backdrop-blur-md"
    />
  );
};
