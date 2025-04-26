import { useLoader } from '@react-three/fiber'
import { MTLLoader, OBJLoader } from 'three-stdlib'
import { useMemo, useRef } from 'react'
import { animated } from '@react-spring/three'

export function ImportedMesh({ path, mtlPath, ...props }) {
  const materials = useLoader(MTLLoader, mtlPath);
  const obj = useLoader(OBJLoader, path, (loader) => {
    materials.preload();
    loader.setMaterials(materials);
  });

  const cloned = useMemo(() => obj.clone(), [obj]);
  const ref = useRef();

  return <animated.primitive object={cloned} ref={ref} {...props} />;
}
