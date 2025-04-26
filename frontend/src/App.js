import { useState, useEffect, useRef } from "react";
import _ from "underscore";
import { Canvas } from "@react-three/fiber";
import { Blob, floorLevel } from "./components/Blob";
import { Platform } from "./components/Platform";
import { OrbitControls, Html, Text } from "@react-three/drei";
import { ImportedMesh } from "./components/ImportedMesh";
import { initialize , getWorldMetrics, wait, proposePolicy} from "./api";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";
import HistoryEduIcon from "@mui/icons-material/HistoryEdu";
import { IconButton } from "@mui/material";
import { useThree, useFrame } from "@react-three/fiber";
import { useControls } from "@react-three/drei";
import StoryPopup from "./components/StoryPopUp";



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
    <div
      style={{
        overflow: "hidden",
        whiteSpace: "nowrap",
        width: "100%",
        background: "darkred",
        color: "white",
        fontSize: "1.2rem",
        padding: "10px 0",
        // marginTop: "20px",
        marginBottom: "10px",
        position: "relative",
      }}
    >
      <div
        ref={tickerRef}
        style={{
          display: "inline-block",
          paddingLeft: "100%",
          whiteSpace: "nowrap",
        }}
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

const generateCleanBlobStories = (numBlobs) => {
  return new Map(
    Array.from({ length: numBlobs }).map((_, index) => [index, "No story available"])
  )
}

function App() {
  // const [numBlobs, setNumBlobs] = useState(0);
  const blobRefs = useRef([]);
  const [initiliazeDict, setInitializeDict] = useState({});
 
  const numBlobs = initiliazeDict.blobs?.length;
  const [blobStories, setBlobStories] = useState(generateCleanBlobStories(numBlobs))
  // Function to generate random target position (x, y, z)
  const generateRandomPosition = () => {
    return [Math.random() * 4.0 - 2.0, floorLevel, Math.random() * 4.0 - 2.0];
  };


  useEffect(() => {
    setGoal(initiliazeDict["metrics"])
  }, [initiliazeDict])
  

  const [gameStarted, setGameStarted] = useState(false);
  const [color, setColor] = useState("white");
  const [goal, setGoal] = useState("Get cleanliness to 80%");
  const [goalReached, setGoalReached] = useState(50);
  const [policy, setPolicy] = useState("");
  const [story, setStory] = useState("");
  const [popupOpen, setPopupOpen] = useState(false);
  const [headlines, setHeadlines] = useState([]);
  const [metrics, setMetrics] = useState({})

  const setStoryPopUp = (story) => {
    setStory(story);
    setPopupOpen(true);
  };

  const handleTimeStepDictionary = (dict) => {
    setMetrics(dict.metrics)
    setBlobStories(generateCleanBlobStories(numBlobs))
    console.log("mydict",dict)
    setBlobStories(dict.event.impacts)
    setHeadlines([dict.event.headline, dict.event.headline_metrics, ...dict.event.subheadlines ])
  }

  useEffect(() => {
    setGoalReached(metrics.environment_cleanliness*100)
  }, [metrics])
  
  // Function to move a specific blob to a random position by its index
  const handleMoveBlob = (index) => {
    const randomPosition = generateRandomPosition();
    blobRefs.current[index].moveToPosition(randomPosition); // Trigger move on the specific blob
  };
  
  const iterationDance = () =>  {
  for (let i = 0; i < numBlobs; i++) {
    handleMoveBlob(i);
  }
}

 

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
        <h1>Goal: Get cleanliness to 80%</h1>

        <Box sx={{ width: "60%" }}>
          <LinearProgress variant="determinate" value={goalReached} />
        </Box>
        {gameStarted ? (
          <Canvas
            camera={{ position: [-0.0, 2, 10], fov: 50 }}
            style={{ width: "100%", height: "65vh", overflow: "hidden" }}
          >
            {/* <LogCamera/> */}
            <Html
              position={[-3, 4, -5]}
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
              occlude={true}
            >
              <div>
                <div>
                  <strong>Blobtopia</strong>
                </div>
                {Object.entries(metrics).map(([key, value]) => (
                  <div key={key}>
                  {(key.charAt(0).toUpperCase() + key.slice(1)).replaceAll("_", " ")}: 
                  {typeof value === "number"
                    ? `${Math.floor(value * 100)}%`
                    : value}
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
            {/* <Blob color="lime" initialX={2} /> */}

            <OrbitControls
              maxPolarAngle={Math.PI / 2 + Math.PI / 9} // 90 + 20 deg
              minPolarAngle={0}
              maxAzimuthAngle={Math.PI / 6} // 30 deg
              minAzimuthAngle={-Math.PI / 6} // -30 deg
            />

            {/* Dynamically render blobs */}
            {Array.from({ length: numBlobs }).map((_, index) => (
              <Blob
                key={index}
                ref={(el) => (blobRefs.current[index] = el)} // Dynamically assign refs
                color={index % 2 === 0 ? "hotpink" : "cyan"}
                initialX={Math.random() * 4.0 - 2.0}
                initialY={Math.random() * 4.0 - 2.0}
                story={"no story rn"}
                showStory={setStoryPopUp}
              />
            ))}

            <OrbitControls
              maxPolarAngle={Math.PI / 2 + Math.PI / 9}
              minPolarAngle={0}
              maxAzimuthAngle={Math.PI / 6}
              minAzimuthAngle={-Math.PI / 6}
            />
          </Canvas>
        ) : (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              height: "65vh",
            }}
          >
            {" "}
            <Button
              variant="contained"
              color="white"
              onClick={() => {
                initialize().then((r) => setInitializeDict(r)); 
                getWorldMetrics().then((r) =>setMetrics(r));
                setGameStarted(true);
              }}
            >
              Start Game
            </Button>{" "}
          </div>
        )}
        <HeadlineTicker
          headlines={Array.from({ length: 100 })
            .map(() => headlines)
            .flat()}
        />
        <div
          style={{
            display: "flex",
            "flex-direction": "row",
            "align-items": "center",
            "justify-content": "space-evenly",
            width: "50%",
          }}
        >
          <Button onClick={()=>{iterationDance(); wait().then((r)=>{handleTimeStepDictionary(r)})}} variant="outlined" style={{ height: "100%" }}>
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
            style={{ width: "40vw" }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={()=>{iterationDance(); proposePolicy(policy).then((r)=>{handleTimeStepDictionary(r)})}} 
                  >
                    {" "}
                    <HistoryEduIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </div>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          
        </div>
        <StoryPopup
          open={popupOpen}
          onClose={() => setPopupOpen(false)}
          story={story}
        />
      </div>
    </div>
  );
}

export default App;
