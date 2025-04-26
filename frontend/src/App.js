import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import _ from 'underscore';
import { Blob } from './components/Blob';
import { Platform } from './components/Platform';
import { OrbitControls } from '@react-three/drei';
import { ImportedMesh } from './components/ImportedMesh';

function App() {
  const [color, setColor] = useState("white")


  const handleClick = () => {
    

  }

  

  return (
    <div className="App">
      <div id="canvas-container" style={{"display":"flex", "flex-direction":"column", "align-items":"center"}}>
      <Canvas camera={{ position: [0, 5, 10], fov: 50 }} style={{ width: "70vw", height: "70vh", overflow: "hidden" }}>
        <ambientLight intensity={0.3} />
        <directionalLight position={[2, 5, 2]} color={color} />
        <Platform color="gray" scale={[1.2, 1, 1.2]} position={[0,0,-3.4]} />
        <Platform color="#32CD32" scale={[2, 1, 2]} />
        <ImportedMesh path="models/city_merged.obj" mtlPath="models/city_merged.mtl" position={[.4,.22,-3.6]} scale={[.2,.25,.2]} rotation={[0,-Math.PI/2, 0]}/>
       
       
        <Blob color="hotpink" initialX={2} />
        <Blob color="cyan" initialX={2} />
        {/* <Blob color="lime" initialX={2} /> */}

        <OrbitControls 
            maxPolarAngle={Math.PI / 2 + Math.PI / 9} // 90 + 20 deg
            minPolarAngle={0} 
            maxAzimuthAngle={Math.PI / 6}             // 30 deg
            minAzimuthAngle={-Math.PI / 6}             // -30 deg
          />
      </Canvas>
      </div>
      <div style={{"display":"flex", "flex-direction":"column", "align-items":"center"}}>
      <button onClick={handleClick}>
        <h1>Do something</h1>
      </button>
        <h1>yee:</h1>
      </div>
    </div>
  );
}

export default App;
