import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import _ from 'underscore';
import { Blob } from './components/Blob';
import { Platform } from './components/Platform';
import { OrbitControls } from '@react-three/drei';

function App() {
  const [color, setColor] = useState("white")


  const handleClick = () => {
    

  }

  

  return (
    <div className="App">
      <div id="canvas-container" style={{"display":"flex", "flex-direction":"column", "align-items":"center"}}>
      <Canvas camera={{ position: [0, 5, 10], fov: 50 }} style={{ width: "60vw", height: "60vh", overflow: "hidden" }}>
        <ambientLight intensity={0.3} />
        <directionalLight position={[2, 5, 2]} color={color} />
        <Platform color="green" scale={[1, 1, 1]} position={[0,0,-5]} />
        <Platform color="green" scale={[2, 1, 2]} />
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
        <h1>Get a new baby</h1>
      </button>
        <h1>yee:</h1>
      </div>
    </div>
  );
}

export default App;
