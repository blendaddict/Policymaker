import { useState, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { Blob, floorLevel } from './components/Blob';
import { Platform } from './components/Platform';
import { OrbitControls } from '@react-three/drei';
import { ImportedMesh } from './components/ImportedMesh';
import { initialize } from './api';

function App() {
  // const [numBlobs, setNumBlobs] = useState(0);
  const blobRefs = useRef([]);
  const [world, setWorld] = useState({})
  const numBlobs = world.blobs?.length

  // Function to generate random target position (x, y, z)
  const generateRandomPosition = () => {
    return [Math.random() * 4.0 - 2.0, floorLevel, Math.random() * 4.0 - 2.0];
  };

  // Function to move a specific blob to a random position by its index
  const handleMoveBlob = (index) => {
    const randomPosition = generateRandomPosition();
    blobRefs.current[index].moveToPosition(randomPosition);  // Trigger move on the specific blob
  };

  return (
    <div className="App">
      <div
        id="canvas-container"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Canvas camera={{ position: [0, 5, 10], fov: 50 }} style={{ width: '70vw', height: '70vh', overflow: 'hidden' }}>
          <ambientLight intensity={0.3} />
          <directionalLight position={[2, 5, 2]} />
          <Platform color="gray" scale={[1.2, 1, 1.2]} position={[0, 0, -3.4]} />
          <Platform color="#32CD32" scale={[2, 1, 2]} />
          <ImportedMesh
            path="models/city_merged.obj"
            mtlPath="models/city_merged.mtl"
            position={[0.4, 0.22, -3.6]}
            scale={[0.2, 0.25, 0.2]}
            rotation={[0, -Math.PI / 2, 0]}
          />

          {/* Dynamically render blobs */}
          {Array.from({ length: numBlobs }).map((_, index) => (
            <Blob
              key={index}
              ref={(el) => (blobRefs.current[index] = el)} // Dynamically assign refs
              color={index % 2 === 0 ? 'hotpink' : 'cyan'}
              initialX={Math.random() * 4.0 - 2.0}
              initialY={Math.random() * 4.0 - 2.0}
            />
          ))}

          <OrbitControls maxPolarAngle={Math.PI / 2 + Math.PI / 9} minPolarAngle={0} maxAzimuthAngle={Math.PI / 6} minAzimuthAngle={-Math.PI / 6} />
        </Canvas>
      </div>
      <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <button onClick={() => initialize().then(r => setWorld(r))}><h1>Initialize</h1></button>
      </div>
    </div>
  );
}

export default App;
