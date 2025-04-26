import { OBJLoader } from 'three/addons/loaders/OBJLoader.js'
import { useLoader } from '@react-three/fiber'
import { useRef, useEffect, useMemo } from 'react'
import * as THREE from 'three'
import { animated, useSpring } from '@react-spring/three'

export function Platform(props) {
    const obj = useLoader(OBJLoader, '/models/platform.obj');
    const ref = useRef();
    let geometry = null;
    obj.traverse((child) => {
      if (child.isMesh && !geometry) {
        geometry = child.geometry.clone();
      }
    })
  
    const material = new THREE.MeshStandardMaterial({color: props.color});

    return <animated.mesh geometry={geometry} ref={ref} material={material} {...props} />;
  }
  