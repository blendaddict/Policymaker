import { useRef, useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export const floorLevel = 0.148310

const Blob = forwardRef(({ color = "white", initialX = 0 }, ref) => {
  const meshRef = useRef();
  const [targetPosition, setTargetPosition] = useState([initialX, floorLevel, 0]);
  const [startTime, setStartTime] = useState(0);
  const [currentPosition, setCurrentPosition] = useState([initialX, floorLevel, 0]); // Track current position

  // Function to update the target position
  const moveToPosition = (newTarget) => {
    setTargetPosition(newTarget);
    setStartTime(performance.now()); // Reset the timer for a smooth move
  };

  // Expose moveToPosition to parent components
  useImperativeHandle(ref, () => ({
    moveToPosition,
  }));

  useEffect(() => {
    if (meshRef.current) {
      setStartTime(performance.now());
    }
  }, [targetPosition]);

  // Animate blob movement
  useFrame(() => {
    if (!meshRef.current || !targetPosition) return;

    const elapsedTime = (performance.now() - startTime) / 1000;
    const [dx, dz] = [currentPosition[0] - targetPosition[0], currentPosition[2] - targetPosition[2]]
    const dist = Math.sqrt(dx*dx + dz*dz)
    let progress = Math.min(elapsedTime / 1.0 / dist, 1);

    if (progress === 1) {
      // When progress is 100%, set the blob's final position
      setCurrentPosition(targetPosition);
      meshRef.current.position.set(targetPosition[0], targetPosition[1], targetPosition[2]);
      return;
    }

    // Calculate the movement from the current position to the target position
    const [jumpLength, jumpHeight] = [0.5, 0.5]
    const numJumps = Math.ceil(dist / jumpLength)
    const x = currentPosition[0] + progress * (targetPosition[0] - currentPosition[0]);
    const y = currentPosition[1] + Math.abs(Math.sin(numJumps * progress * Math.PI)) * jumpHeight;
    const z = currentPosition[2] + progress * (targetPosition[2] - currentPosition[2]);

    meshRef.current.position.set(x, y, z);
  });

  return (
    <mesh
      ref={meshRef}
      geometry={new THREE.SphereGeometry(1, 32, 32)} // Placeholder geometry for the blob
      material={new THREE.MeshStandardMaterial({ color })}
      scale={[0.1, 0.1, 0.1]}
    />
  );
});

export { Blob };
