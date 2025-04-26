import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import _ from 'underscore';
import { Blob } from './components/Blob';

function App() {
  const [color, setColor] = useState("red")
  const [jumpTrigger, setJumpTrigger] = useState(false)
  const [rate, Rate] = useState(0)

  const handleClick = () => {
    setColor(_.sample(["red", "green" , "black", "orange", "white"]))
    setJumpTrigger(true)
    setTimeout(() => setJumpTrigger(false), 50) // reset the trigger so it can animate again next click

  }

  useEffect(() => {
    if(jumpTrigger) {
    
  }
    
  }, [jumpTrigger])
  

  return (
    <div className="App">
      <div id="canvas-container">
        <Canvas>
          <ambientLight intensity={0.3} />
          <directionalLight position={[0, 0, 5]} color={color} />
          <Blob color={color} jumpTrigger={jumpTrigger} />
        </Canvas>
      </div>
      <div style={{"display":"flex", "flex-direction":"column", "align-items":"center"}}>
      <button onClick={handleClick}>
        <h1>Get a new baby</h1>
      </button>
        <h1>yee: {rate}%</h1>
      </div>
    </div>
  );
}

export default App;
