import { useRef, useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { useLoader, useFrame } from '@react-three/fiber';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import * as THREE from 'three';
import { animated, useSpring } from '@react-spring/three';

export const floorLevel = 0.22 // 0.148310;

const Blob = forwardRef(({ color = "white", initialX = 0 }, ref) => {
  const obj = useLoader(OBJLoader, '/models/blob.obj');  // Load the .obj model
  const meshRef = useRef();
  const [targetPosition, setTargetPosition] = useState([initialX, floorLevel, 0]);
  const [startTime, setStartTime] = useState(0);
  const [currentPosition, setCurrentPosition] = useState([initialX, floorLevel, 0]); // Track current position

  let geometry = null;
  // Extract geometry from the loaded OBJ model
  obj.traverse((child) => {
    if (child.isMesh && !geometry) {
      geometry = child.geometry.clone();
    }
  });

  // Material for the mesh
  const material = new THREE.MeshStandardMaterial({ color });

  // Spring-based animation (use spring for smooth position transitions)
  const { position } = useSpring({
    from: { position: [initialX, 0.5, 0] },
    to: async (next) => {
      while (true) {
        await next({ position: [initialX + 2, 0.5, 0] });
        await next({ position: [initialX - 2, 0.5, 0] });
      }
    },
    config: { duration: 2000 },
  });

  // Expose moveToPosition to parent components to trigger movement
  const moveToPosition = (newTarget) => {
    setTargetPosition(newTarget);
    setStartTime(performance.now());  // Reset the timer for smooth movement
  };

  // Expose moveToPosition through ref
  useImperativeHandle(ref, () => ({
    moveToPosition,
  }));

  // Handle the movement animation in a frame-based approach
  useEffect(() => {
    if (meshRef.current) {
      setStartTime(performance.now());
    }
  }, [targetPosition]);

  // Animate blob movement on each frame
  useFrame(() => {
    if (!meshRef.current || !targetPosition) return;

    const elapsedTime = (performance.now() - startTime) / 1000;
    const [dx, dz] = [currentPosition[0] - targetPosition[0], currentPosition[2] - targetPosition[2]];
    const dist = Math.sqrt(dx * dx + dz * dz);
    let progress = Math.min(elapsedTime / 1.0 / dist, 1);

    if (progress === 1) {
      // When progress is 100%, set the blob's final position
      setCurrentPosition(targetPosition);
      meshRef.current.position.set(targetPosition[0], targetPosition[1], targetPosition[2]);
      return;
    }

    // Calculate the movement from the current position to the target position
    const [jumpLength, jumpHeight] = [0.5, 0.3];
    const numJumps = Math.ceil(dist / jumpLength);
    const x = currentPosition[0] + progress * (targetPosition[0] - currentPosition[0]);
    const y = currentPosition[1] + Math.abs(Math.sin(numJumps * progress * Math.PI)) * jumpHeight;
    const z = currentPosition[2] + progress * (targetPosition[2] - currentPosition[2]);

    meshRef.current.position.set(x, y, z);
  });

  // If geometry is not found yet, don't render anything
  if (!geometry) return null;

  return (
    <animated.mesh
      ref={meshRef}
      geometry={geometry}
      material={material}
      position={position}
      scale={[0.1, 0.1, 0.1]}
    />
  );
});

export { Blob };
