// Template: the same character craft, frame-driven for Remotion (CSS animations/transitions do NOT render).
// Usage: <Sequence from={0} durationInFrames={120}><MascotScene jumpAt={30} waveAt={75} /></Sequence>
import React from "react";
import { AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig } from "remotion";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const MascotScene: React.FC<{ jumpAt?: number; waveAt?: number; seed?: string }> = ({ jumpAt = 30, waveAt = 75, seed = "mascot" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame - jumpAt; // frames are at 30fps: 4f crouch, 10f rise, 8f fall, 2f impact, then spring settle

  const crouch = interpolate(t, [0, 4], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) }) * (t < 4 ? 1 : 0);
  const rise = interpolate(t, [4, 14], [0, 1], { ...clamp, easing: Easing.out(Easing.sin) });
  const fall = interpolate(t, [14, 22], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const y = -96 * rise + 96 * fall;
  const impact = t >= 22 ? spring({ frame: t - 22, fps, config: { damping: 7, stiffness: 220, mass: 0.6 } }) : 1;
  const squashY = t < 4 ? 1 - 0.14 * crouch : t >= 22 ? 0.84 + 0.16 * impact : 1 + 0.06 * Math.sin(Math.PI * rise) * (1 - fall);
  const squashX = 1 / Math.sqrt(squashY); // keep volume

  // Idle breathing between actions (slow sine), deterministic.
  const breath = 1 + 0.02 * Math.sin((frame / fps) * Math.PI * 0.6);

  // Seeded blinks: pick blink frames once, deterministically.
  const blinkFrames = Array.from({ length: 6 }, (_, i) => Math.floor(20 + i * 45 + random(`${seed}-blink-${i}`) * 30));
  const blinking = blinkFrames.some((b) => frame >= b && frame < b + 4);

  // Wave: anticipation dip, overshoot, three oscillations, settle.
  const w = frame - waveAt;
  const armR = w < 0 ? 0 : interpolate(w, [0, 3, 10, 14, 18, 22, 26, 36], [0, 15, -140, -110, -140, -110, -130, 0], { ...clamp, easing: Easing.inOut(Easing.sin) });

  return (
    <AbsoluteFill style={{ background: "var(--ground, #E8EEF2)", justifyContent: "center", alignItems: "center" }}>
      <svg viewBox="0 0 400 320" width={800} height={640}>
        <ellipse cx={200} cy={286} rx={70 * (1 - 0.45 * rise + 0.45 * fall)} ry={10} fill="#14212B" opacity={0.18 - 0.1 * rise + 0.1 * fall} />
        <g transform={`translate(0 ${y}) translate(200 282) scale(${squashX} ${squashY}) translate(-200 -282)`}>
          <rect x={104} y={170} width={44} height={20} rx={10} fill="#B9471F" />
          <g transform={`rotate(${armR} 254 180)`}><rect x={252} y={170} width={44} height={20} rx={10} fill="#B9471F" /></g>
          <rect x={160} y={262} width={26} height={20} rx={6} fill="#B9471F" />
          <rect x={214} y={262} width={26} height={20} rx={6} fill="#B9471F" />
          <g transform={`translate(200 270) scale(1 ${breath}) translate(-200 -270)`}>
            <rect x={132} y={120} width={136} height={150} rx={44} fill="#F06A3A" />
            <rect x={170} y={blinking ? 180 : 170} width={14} height={blinking ? 3 : 22} rx={3} fill="#14212B" />
            <rect x={216} y={blinking ? 180 : 170} width={14} height={blinking ? 3 : 22} rx={3} fill="#14212B" />
            <path d="M188 212 Q200 222 212 212" stroke="#14212B" strokeWidth={5} fill="none" strokeLinecap="round" />
          </g>
        </g>
      </svg>
    </AbsoluteFill>
  );
};
