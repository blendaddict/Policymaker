import { useState, useEffect } from "react";
import { Canvas } from "@react-three/fiber";
import _ from "underscore";
import { Blob } from "./components/Blob";
import { Platform } from "./components/Platform";
import { OrbitControls } from "@react-three/drei";
import { ImportedMesh } from "./components/ImportedMesh";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";
import HistoryEduIcon from "@mui/icons-material/HistoryEdu";
import { IconButton } from '@mui/material';
import { Text } from '@react-three/drei';
import { Html } from '@react-three/drei';


const metrics = {
  happiness: 40,
  extremism: 20,
};

function App() {
  const [color, setColor] = useState("white");
  const [goal, setGoal] = useState("Reduce trash in the environment");
  const [goalReached, setGoalReached] = useState(50);
  const [policy, setPolicy] = useState("")
  useEffect(() => {
    const timer = setInterval(() => {
      setGoalReached((oldProgress) => {
        if (oldProgress === 100) {
          return 0;
        }
        const diff = Math.random() * 10;
        return Math.min(oldProgress + diff, 100);
      });
    }, 500);

    return () => {
      clearInterval(timer);
    };
  }, []);

  return (
    <div className="App">
      <div
        id="canvas-container"
        style={{
          display: "flex",
          "flex-direction": "column",
          "align-items": "center",
        }}
      >
        <h1>Goal: {goal}</h1>

        <Box sx={{ width: "60%" }}>
          <LinearProgress variant="determinate" value={goalReached} />
        </Box>

        <Canvas
          camera={{ position: [0, 5, 10], fov: 50 }}
          style={{ width: "70vw", height: "70vh", overflow: "hidden" }}
        > 
          <Html
    position={[-3, 4., -4]}
    style={{
      color: "white",
      background: "rgba(0,0,0,0.5)",
      padding: "10px",
      borderRadius: "8px",
      fontFamily: "monospace",
      fontSize: "14px",
      pointerEvents: "none",
      userSelect: "none",
    }}
    transform
    occlude={false}
  >
    <div>
      <div><strong>Blobtopia</strong></div>
      {Object.entries(metrics).map(([key, value]) => (
        <div key={key}>
          {key.charAt(0).toUpperCase() + key.slice(1)}: {value}
        </div>
      ))}
    </div>
  </Html>

          <ambientLight intensity={0.3} />
          <directionalLight position={[2, 5, 2]} color={color} />
          <Platform
            color="gray"
            scale={[1.2, 1, 1.2]}
            position={[0, 0, -3.4]}
          />
          <Platform color="#32CD32" scale={[2, 1, 2]} />
          <ImportedMesh
            path="models/city_merged.obj"
            mtlPath="models/city_merged.mtl"
            position={[0.4, 0.22, -3.6]}
            scale={[0.2, 0.25, 0.2]}
            rotation={[0, -Math.PI / 2, 0]}
          />
          <Blob color="hotpink" initialX={2} />
          <Blob color="cyan" initialX={2} />
          {/* <Blob color="lime" initialX={2} /> */}

          <OrbitControls
            maxPolarAngle={Math.PI / 2 + Math.PI / 9} // 90 + 20 deg
            minPolarAngle={0}
            maxAzimuthAngle={Math.PI / 6} // 30 deg
            minAzimuthAngle={-Math.PI / 6} // -30 deg
          />
        </Canvas>
        <div
          style={{
            display: "flex",
            "flex-direction": "row",
            "align-items": "center",
            "justify-content": "space-evenly",
            width: "50%",
          }}
        >
          <Button variant="outlined" style={{ height: "100%" }}>
            Wait
          </Button>
          <h3>or</h3>
          <TextField
            value={policy}
            onChange={(event) => {
              setPolicy(event.target.value);
            }}

            label="New Policy"
            variant="outlined"
            style={{width:"40vw"}}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton>  <HistoryEduIcon /></IconButton>
                </InputAdornment>
              ),
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
