'use client';

import React, { useEffect, useRef } from 'react';

interface AudioWaveformProps {
  mode: 'idle' | 'recording' | 'thinking' | 'speaking';
  audioElement?: HTMLAudioElement | null;
}

export default function AudioWaveform({ mode, audioElement }: AudioWaveformProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let phase = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const width = canvas.width;
      const height = canvas.height;
      const centerY = height / 2;
      const barCount = 42;
      const barWidth = 4;
      const gap = (width - barCount * barWidth) / (barCount - 1);

      phase += 0.08;

      for (let i = 0; i < barCount; i++) {
        let amplitude = 6;

        if (mode === 'recording') {
          // Dynamic active waveform
          const wave1 = Math.sin(phase + i * 0.35);
          const wave2 = Math.cos(phase * 1.5 + i * 0.2);
          amplitude = Math.max(8, (wave1 + wave2 + 2) * 16);
        } else if (mode === 'speaking') {
          // AI voice cadence
          const wave = Math.sin(phase * 1.2 + i * 0.45);
          amplitude = Math.max(10, Math.abs(wave) * 38);
        } else if (mode === 'thinking') {
          // Pulsing wave
          const wave = Math.sin(phase * 2 + i * 0.15);
          amplitude = Math.max(6, (wave + 1) * 12);
        } else {
          // Idle ambient gentle wave
          amplitude = 6 + Math.sin(phase * 0.5 + i * 0.1) * 3;
        }

        // Color gradients - Strictly 3-color palette: Slate, Blue shades, White
        let fillStyle = '#334155';
        if (mode === 'recording') {
          fillStyle = i % 2 === 0 ? '#60a5fa' : '#3b82f6'; // Bright blue
        } else if (mode === 'speaking') {
          fillStyle = i % 2 === 0 ? '#2563eb' : '#1d4ed8'; // Royal blue
        } else if (mode === 'thinking') {
          fillStyle = i % 2 === 0 ? '#93c5fd' : '#bfdbfe'; // Soft ice blue
        }

        const x = i * (barWidth + gap);
        const barHeight = Math.min(height - 10, amplitude);
        const y = centerY - barHeight / 2;

        ctx.fillStyle = fillStyle;
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, barHeight, 4);
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [mode, audioElement]);

  return (
    <div
      className="w-full flex flex-col items-center justify-center p-3 rounded-2xl border"
      style={{
        backgroundColor: 'var(--bg-subtle)',
        borderColor: 'var(--border-subtle)',
      }}
    >
      <canvas
        ref={canvasRef}
        width={420}
        height={70}
        className="w-full max-w-[420px] h-[70px]"
      />
      <div className="flex items-center gap-2 mt-2 text-xs font-semibold">
        {mode === 'idle' && (
          <span style={{ color: 'var(--text-muted)' }}>Tayyor holatda • Mikrofon tugmasini bosing</span>
        )}
        {mode === 'recording' && (
          <span className="text-blue-400 flex items-center gap-1.5 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-blue-400" />
            Fuqaro nutqi yozilmoqda...
          </span>
        )}
        {mode === 'thinking' && (
          <span className="text-blue-200 flex items-center gap-1.5 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-blue-300" />
            AI vazirlik nizomlaridan javob shakllantirmoqda...
          </span>
        )}
        {mode === 'speaking' && (
          <span className="text-blue-300 flex items-center gap-1.5 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            Vazir AI javob bermoqda (Madina ovozi)
          </span>
        )}
      </div>
    </div>
  );
}
