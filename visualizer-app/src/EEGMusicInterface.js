import React, { useEffect, useRef, useState } from 'react';

const EEGMusicInterface = () => {
  const canvasRef = useRef(null);
  const [brainwaveData, setBrainwaveData] = useState({
    alpha: 0,
    beta: 0,
    gamma: 0
  });
  const [stress, setStress] = useState(50);
  const [focus, setFocus] = useState(50);

  // Simulate brainwave data generation
  const simulateBrainwaveData = () => {
    setBrainwaveData({
      alpha: Math.random() * 100,
      beta: Math.random() * 100,
      gamma: Math.random() * 100
    });
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const drawVisualizer = () => {
      const WIDTH = canvas.width;
      const HEIGHT = canvas.height;
      const centerX = WIDTH / 2;
      const centerY = HEIGHT / 2;
      const barCount = 60;
      const maxRadius = Math.min(WIDTH, HEIGHT) / 3;

      ctx.clearRect(0, 0, WIDTH, HEIGHT);

      const audioData = Array.from({ length: barCount }, () => Math.random() * 100);

      audioData.forEach((value, i) => {
        const angle = (i / barCount) * Math.PI * 2;
        const barHeight = value * 1.5;
        const barWidth = 8;

        const x = centerX + Math.cos(angle) * maxRadius;
        const y = centerY + Math.sin(angle) * maxRadius;
        const endX = centerX + Math.cos(angle) * (maxRadius + barHeight);
        const endY = centerY + Math.sin(angle) * (maxRadius + barHeight);

        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(endX, endY);
        ctx.strokeStyle = `hsla(${i * 6}, 100%, 50%, 0.7)`;
        ctx.lineWidth = barWidth;
        ctx.stroke();
      });

      animationFrameId = requestAnimationFrame(drawVisualizer);
    };

    drawVisualizer();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  useEffect(() => {
    const intervalId = setInterval(simulateBrainwaveData, 1000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div style={styles.container}>
      <div style={styles.backgroundGradient}></div>
      <div style={styles.canvasContainer}>
        <canvas ref={canvasRef} style={styles.canvas} />
        <div style={styles.brainwaveChart}>
          <svg style={styles.waves} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 20">
            <path
              d="M0,10 Q5,15 10,10 T 20,10 T 30,10 T 40,10 T 50,10 T 60,10 T 70,10 T 80,10 T 90,10 T 100,10"
              stroke="blue"
              strokeWidth="0.5"
              fill="transparent"
              style={{ transform: `scaleY(${brainwaveData.alpha / 100})` }}
            />
            <path
              d="M0,12 Q5,17 10,12 T 20,12 T 30,12 T 40,12 T 50,12 T 60,12 T 70,12 T 80,12 T 90,12 T 100,12"
              stroke="green"
              strokeWidth="0.5"
              fill="transparent"
              style={{ transform: `scaleY(${brainwaveData.beta / 100})` }}
            />
            <path
              d="M0,14 Q5,19 10,14 T 20,14 T 30,14 T 40,14 T 50,14 T 60,14 T 70,14 T 80,14 T 90,14 T 100,14"
              stroke="red"
              strokeWidth="0.5"
              fill="transparent"
              style={{ transform: `scaleY(${brainwaveData.gamma / 100})` }}
            />
          </svg>
          <div style={styles.dataDisplay}>
            <h4>Alpha: {brainwaveData.alpha.toFixed(2)}</h4>
            <h4>Beta: {brainwaveData.beta.toFixed(2)}</h4>
            <h4>Gamma: {brainwaveData.gamma.toFixed(2)}</h4>
          </div>
        </div>
      </div>
      <div style={styles.progressBars}>
        <div style={styles.progressBarContainer}>
          <label style={styles.label}>Stress Level</label>
          <div style={styles.progressBar}>
            <div style={{ ...styles.progress, width: `${stress}%`, backgroundColor: 'red' }}></div>
          </div>
        </div>
        <div style={styles.progressBarContainer}>
          <label style={styles.label}>Focus Level</label>
          <div style={styles.progressBar}>
            <div style={{ ...styles.progress, width: `${focus}%`, backgroundColor: 'green' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: '#1e1b4b',
    color: 'white',
    padding: '16px',
    position: 'relative',
    overflow: 'hidden',
  },
  backgroundGradient: {
    position: 'absolute',
    inset: 0,
    background: 'linear-gradient(to bottom right, #1e1b4b, #312e81, #3730a3)',
    opacity: 0.5,
  },
  canvasContainer: {
    flexGrow: 1,
    position: 'relative',
  },
  canvas: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
  },
  brainwaveChart: {
    position: 'relative',
    zIndex: 10,
  },
  waves: {
    width: '100%',
    height: '100%',
  },
  dataDisplay: {
    position: 'absolute',
    bottom: 20,
    left: '50%',
    transform: 'translateX(-50%)',
    color: 'white',
  },
  progressBars: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '16px',
  },
  progressBarContainer: {
    width: '48%',
  },
  label: {
    marginBottom: '4px',
  },
  progressBar: {
    backgroundColor: 'gray',
    borderRadius: '9999px',
    height: '16px',
    overflow: 'hidden',
  },
  progress: {
    height: '100%',
    borderRadius: '9999px',
  },
};

export default EEGMusicInterface;
