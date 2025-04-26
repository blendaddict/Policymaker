import { OBJLoader } from 'three/addons/loaders/OBJLoader.js'
import { useLoader } from '@react-three/fiber'
import { useRef, useEffect } from 'react'
import * as THREE from 'three'
import { animated, useSpring } from '@react-spring/three'


export function Blob({ color = "white", initialX = 0 }) {
  const obj = useLoader(OBJLoader, '/models/blob.obj');
  const ref = useRef();

  useEffect(() => {
    if (ref.current) {
      ref.current.traverse((child) => {
        if (child.isMesh) {
          child.material = new THREE.MeshStandardMaterial({ color });
        }
      });
    }
  }, [obj, color]);

  const { position } = useSpring({
    from: { position: [initialX, 0.5, 0] },
    to: async (next) => {
      while (true) {
        await next({ position: [initialX + 2, 0.5, 0] });
        await next({ position: [initialX - 2, 0.5, 0] });
      }
    },
    config: { duration: 2000 }, // speed of walk
  });

  return <animated.primitive object={obj} ref={ref} position={position} scale={[0.1, 0.1, 0.1]}  />;
}
