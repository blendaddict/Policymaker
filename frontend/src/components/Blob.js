import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { useLoader } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';
import { animated, useSpring } from '@react-spring/three';

export function Blob({ color = "white", initialX = 0 }) {
  const obj = useLoader(OBJLoader, '/models/blob.obj');
  const ref = useRef();

  // Extract the first mesh's geometry from the loaded object
  let geometry = null;
  obj.traverse((child) => {
    if (child.isMesh && !geometry) {
      geometry = child.geometry.clone();
    }
  })

  const material = new THREE.MeshStandardMaterial({ color });

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

  if (!geometry) return null;

  return (
    <animated.mesh
      ref={ref}
      geometry={geometry}
      material={material}
      position={position}
      scale={[0.1, 0.1, 0.1]}
    />
  );
}
