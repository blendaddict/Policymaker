import { OBJLoader } from 'three/addons/loaders/OBJLoader.js'
import { useLoader } from '@react-three/fiber'
import { useRef, useEffect, useMemo } from 'react'
import * as THREE from 'three'
import { animated, useSpring } from '@react-spring/three'

export function Platform(props) {
    const obj = useLoader(OBJLoader, '/models/platform.obj');
    const ref = useRef();
    const cloned = obj.clone()

    return <animated.primitive object={cloned} ref={ref} {...props} />;
  }
  