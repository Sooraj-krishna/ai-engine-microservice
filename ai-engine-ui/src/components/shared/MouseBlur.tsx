'use client';

import { useEffect, useState } from 'react';

export function MouseBlur() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
      if (!isVisible) setIsVisible(true);
    };

    const handleMouseLeave = () => {
      setIsVisible(false);
    };

    window.addEventListener('mousemove', handleMouseMove);
    document.body.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      document.body.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [isVisible]);

  return (
    <div
      className="pointer-events-none fixed z-50 transition-opacity duration-300"
      style={{
        left: `${mousePosition.x}px`,
        top: `${mousePosition.y}px`,
        opacity: isVisible ? 1 : 0,
      }}
    >
      {/* Outer glow */}
      <div
        className="absolute -translate-x-1/2 -translate-y-1/2"
        style={{
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, transparent 70%)',
          filter: 'blur(60px)',
        }}
      />
      
      {/* Inner glow */}
      <div
        className="absolute -translate-x-1/2 -translate-y-1/2"
        style={{
          width: '200px',
          height: '200px',
          background: 'radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%)',
          filter: 'blur(30px)',
        }}
      />
      
      {/* Core cursor dot */}
      <div
        className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full"
        style={{
          width: '4px',
          height: '4px',
          background: 'rgba(255, 255, 255, 0.5)',
          boxShadow: '0 0 20px rgba(255, 255, 255, 0.3)',
        }}
      />
    </div>
  );
}
