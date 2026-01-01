import React from 'react';

const RadarOverlay = () => {
  return (
    <div className="absolute inset-0 pointer-events-none z-[1001] overflow-hidden">
      {/* Radar Scanning Line */}
      <div className="absolute top-1/2 left-1/2 w-[200%] aspect-square -translate-x-1/2 -translate-y-1/2">
        <div className="w-full h-full animate-radar-spin bg-[conic-gradient(from_0deg,transparent_0deg,rgba(0,240,255,0.2)_350deg,rgba(0,240,255,0.5)_360deg)] rounded-full"></div>
      </div>

      {/* Concentric Circles */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[20%] aspect-square border border-[#00f0ff]/20 rounded-full"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[40%] aspect-square border border-[#00f0ff]/20 rounded-full"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] aspect-square border border-[#00f0ff]/20 rounded-full"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] aspect-square border border-[#00f0ff]/20 rounded-full"></div>

      {/* Crosshairs */}
      <div className="absolute top-1/2 left-0 w-full h-[1px] bg-[#00f0ff]/20"></div>
      <div className="absolute top-0 left-1/2 w-[1px] h-full bg-[#00f0ff]/20"></div>

      {/* Random Blips (Simulated) */}
      <div className="absolute top-[30%] left-[40%] w-2 h-2 bg-[#ff003c] rounded-full animate-ping"></div>
      <div className="absolute top-[60%] left-[70%] w-2 h-2 bg-[#00ff00] rounded-full animate-pulse"></div>
      <div className="absolute top-[20%] left-[80%] w-2 h-2 bg-[#00f0ff] rounded-full animate-pulse"></div>
    </div>
  );
};

export default RadarOverlay;
