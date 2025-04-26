import { OBJLoader } from 'three/addons/loaders/OBJLoader.js'
import { useLoader } from '@react-three/fiber'
import { useRef, useEffect } from 'react'
import * as THREE from 'three'
import { animated, useSpring } from '@react-spring/three'

export function Blob({ color, jumpTrigger }) {
  const obj = useLoader(OBJLoader, '/models/blob.obj')
  const ref = useRef()

  useEffect(() => {
    if (ref.current) {
      ref.current.traverse((child) => {
        if (child.isMesh) {
          child.material = new THREE.MeshStandardMaterial({ color: color })
        }
      })
    }
  }, [obj, color])

  const { position, rotation } = useSpring({
    from: { position: [0, 0, 0], rotation: [0, 0, 0] },
    to: async (next) => {
      if (jumpTrigger) {
        await next({ position: [0, 1, 0], rotation: [0, Math.PI * 2, 0] }) // Jump up + full 360 spin
        await next({ position: [0, 0, 0], rotation: [0, 0, 0] }) // Fall back down
      }
    },
    reset: jumpTrigger,
    config: { mass: 1, tension: 300, friction: 15 },
  })

  return <animated.primitive object={obj} ref={ref} position={position} rotation={rotation} />
}
