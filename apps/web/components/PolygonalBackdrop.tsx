/**
 * Decorative polygonal SVG background for the public auth surface.
 * Pure decoration; aria-hidden. No PII, no client state.
 */
export function PolygonalBackdrop() {
  return (
    <svg
      aria-hidden
      role="presentation"
      className="pointer-events-none absolute inset-0 -z-10 h-full w-full"
      preserveAspectRatio="xMidYMid slice"
      viewBox="0 0 1440 900"
    >
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#0F172A" />
          <stop offset="55%" stopColor="#1B3A5B" />
          <stop offset="100%" stopColor="#005EA2" />
        </linearGradient>
      </defs>
      <rect width="1440" height="900" fill="url(#bg)" />
      <g fill="white" fillOpacity="0.04">
        <polygon points="0,0 380,0 200,260" />
        <polygon points="380,0 780,0 580,200 200,260" />
        <polygon points="780,0 1180,0 980,280 580,200" />
        <polygon points="1180,0 1440,0 1440,260 980,280" />
        <polygon points="200,260 580,200 380,520 60,520" />
        <polygon points="580,200 980,280 820,560 380,520" />
        <polygon points="980,280 1440,260 1440,560 820,560" />
        <polygon points="60,520 380,520 200,860 0,900" />
        <polygon points="380,520 820,560 640,900 200,860" />
        <polygon points="820,560 1440,560 1440,900 640,900" />
      </g>
    </svg>
  );
}
