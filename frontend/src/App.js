import { useState, useEffect, useRef} from "react";
import { Canvas } from "@react-three/fiber";
import _ from "underscore";
import { Blob } from "./components/Blob";
import { Platform } from "./components/Platform";
import { OrbitControls, Html, Text } from '@react-three/drei'
import { ImportedMesh } from "./components/ImportedMesh";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";
import HistoryEduIcon from "@mui/icons-material/HistoryEdu";
import { IconButton } from '@mui/material';
import { useThree,useFrame  } from '@react-three/fiber'
import { useControls } from '@react-three/drei'


const metrics = {
  happiness: 40,
  extremism: 20,
};

function LogCamera() {
  const { camera } = useThree()

  useFrame(() => {
    console.log('camera.matrixWorld:', camera.matrixWorld.elements)
  })

  return null
}

function HeadlineTicker({ headlines }) {
  const tickerRef = useRef();

  useEffect(() => {
    let offset = 0;
    const speed = 3;
    const interval = setInterval(() => {
      if (tickerRef.current) {
        offset -= speed;
        tickerRef.current.style.transform = `translateX(${offset}px)`;

        if (Math.abs(offset) >= tickerRef.current.scrollWidth / 2) {
          offset = 0;
        }
      }
    }, 30);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{
      overflow: "hidden",
      whiteSpace: "nowrap",
      width: "100%",
      background: "black",
      color: "white",
      fontSize: "1.2rem",
      padding: "10px 0",
      // marginTop: "20px",
      marginBottom:"10px",
      position: "relative"
    }}>
      <div
        ref={tickerRef}
        style={{ display: "inline-block", paddingLeft: "100%", whiteSpace: "nowrap" }}
      >
        {[...headlines, ...headlines].map((headline, idx) => (
          <span key={idx} style={{ marginRight: "50px" }}>
            {headline}
          </span>
        ))}
      </div>
    </div>
  );
}


function App() {
  const [color, setColor] = useState("white");
  const [goal, setGoal] = useState("Reduce trash in the environment");
  const [goalReached, setGoalReached] = useState(50);
  const [policy, setPolicy] = useState("")
  const blobRef1 = useRef();
  const blobRef2 = useRef();


  // Function to generate random target position (x, y, z)
  const generateRandomPosition = () => {
    return [Math.random() * 5 - 2.5, .22, Math.random() * 5 - 2.5]; // Random x and z between -2.5 and 2.5, with y=0
  };


  const headlines = [
    "Breaking: Blobtopia reaches 40% happiness!",
    "New Policy Proposed: Less Trash!",
    "Cyan Blob Moves East!",
    "Hotpink Blob Dances!",
    "City Expansion Underway...",
    "Pollution Levels Drop by 5%",
  ];
  
  // Function to move a specific blob to a random position
  const handleMoveBlob = (blobRef) => {
    const randomPosition = generateRandomPosition();
    blobRef.current.moveToPosition(randomPosition);  // Trigger move on the specific blob
  };
  
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
          
          camera={{ position: [-0.0, 7.3156, 7.0145], fov: 50 }}
          style={{ width: "100%", height: "65vh", overflow: "hidden" }}
        > 
        <LogCamera/>
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
           <Blob ref={blobRef1} color="hotpink" initialX={2} />
        <Blob ref={blobRef2} color="cyan" initialX={2} />
          {/* <Blob color="lime" initialX={2} /> */}

          <OrbitControls
            maxPolarAngle={Math.PI / 2 + Math.PI / 9} // 90 + 20 deg
            minPolarAngle={0}
            maxAzimuthAngle={Math.PI / 6} // 30 deg
            minAzimuthAngle={-Math.PI / 6} // -30 deg
          />
        </Canvas>
        <HeadlineTicker headlines={ Array.from({ length: 100 })
  .map(() => headlines)
  .flat()} />
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
        {/* <div style={{"display":"flex", direction:"row"}}>
          <button onClick={() => handleMoveBlob(blobRef1)}>
          <h1>Move Hotpink Blob</h1>
        </button>
        <button onClick={() => handleMoveBlob(blobRef2)}>
          <h1>Move Cyan Blob</h1>
        </button>
        </div> */}
      </div>
    </div>
  );
}

export default App;