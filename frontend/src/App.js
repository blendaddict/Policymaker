import { useState, useEffect, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import { Blob, floorLevel } from "./components/Blob";
import { Platform } from "./components/Platform";
import { OrbitControls, Html , Billboard } from "@react-three/drei";
import { ImportedMesh } from "./components/ImportedMesh";
import { Sky} from "@react-three/drei";
import {
  initialize,
  getBlobInformation,
  getWorldMetrics,
  wait,
  proposePolicy,
} from "./api";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import LinearProgress from "@mui/material/LinearProgress";
import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";
import HistoryEduIcon from "@mui/icons-material/HistoryEdu";
import { SortingDropdown } from './components/SortingDropdown'
import { sortBlobs } from './sortBlobs'
import { IconButton } from "@mui/material";
import StoryPopup from "./components/StoryPopUp";

/**
 * Helper – returns a Map where every blob index (0‒numBlobs-1)
 * is present. Blobs without a story get the placeholder text.
 */
const PLACEHOLDER = "No story yet 🙃";
const makeBlobStories = (numBlobs, impacts = {}) => {
  const map = new Map();
  for (let i = 0; i < numBlobs; i++) {
    map.set(i, impacts[i] ?? PLACEHOLDER);
  }
  return map;
};

function HeadlineTicker({ headlines }) {
  const tickerRef = useRef();
  useEffect(() => {
    let offset = 0;
    const speed = 3;
    const id = setInterval(() => {
      if (tickerRef.current) {
        offset -= speed;
        tickerRef.current.style.transform = `translateX(${offset}px)`;
        if (Math.abs(offset) >= tickerRef.current.scrollWidth / 2) offset = 0;
      }
    }, 30);
    return () => clearInterval(id);
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
        marginBottom: "10px",
      }}
    >
      <div
        ref={tickerRef}
        style={{ display: "inline-block", paddingLeft: "100%", whiteSpace: "nowrap" }}
      >
        {[...headlines, ...headlines].map((h, i) => (
          <span key={i} style={{ marginRight: "50px" }}>
            {h}
          </span>
        ))}
      </div>
    </div>
  );
}

function App() {
  const blobRefs = useRef([]);
  const [initializeDict, setInitializeDict] = useState({});
  const numBlobs = initializeDict.blobs?.length || 0;
  const [blobStories, setBlobStories] = useState(new Map());
  const [gameStarted, setGameStarted] = useState(false);
  const [goalReached, setGoalReached] = useState(50);
  const [policy, setPolicy] = useState("");
  const [story, setStory] = useState("");
  const [popupOpen, setPopupOpen] = useState(false);
  const [headlines, setHeadlines] = useState([]);
  const [metrics, setMetrics] = useState({});
  
  function sortBlobsByCriterion(category) {
    getBlobInformation().then(b =>sortBlobs(b, blobRefs, category))
  }
  
  const setStoryPopUp = (s) => {
    setStory(s);
    setPopupOpen(true);
  };

  const handleTimeStepDictionary = (dict) => {
    setMetrics(dict.metrics);
    const impacts = dict.event?.impacts || {};
    setBlobStories(makeBlobStories(numBlobs, impacts));
    setHeadlines([
      dict.event.headline,
      dict.event.headline_metrics,
      ...(dict.event.subheadlines || []),
    ]);
  };

  useEffect(() => {
    if (typeof metrics.environment_cleanliness === "number")
      setGoalReached(metrics.environment_cleanliness * 100);
  }, [metrics]);

  useEffect(() => {
    if (numBlobs) setBlobStories(makeBlobStories(numBlobs));
  }, [numBlobs]);

  const generateRandomPosition = () => [
    Math.random() * 4.0 - 2.0,
    floorLevel,
    Math.random() * 4.0 - 2.0,
  ];
  const handleMoveBlob = (i) => {
    const pos = generateRandomPosition();
    blobRefs.current[i]?.moveToPosition(pos);
  };
  const iterationDance = () => {
    for (let i = 0; i < numBlobs; i++) handleMoveBlob(i);
  };

  return (
    <div className="App">
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <h1>Goal: Get cleanliness to 80%</h1>
        <Box sx={{ width: "60%" }}>
          <LinearProgress variant="determinate" value={goalReached} />
        </Box>
        {gameStarted ? (
          <Canvas camera={{ position: [-0.0, 2, 10], fov: 50 }} style={{ width: "100%", height: "65vh" }} onCreated={({ gl }) => {
            gl.toneMappingExposure = 0.5;   // matches your “exposure” slider
          }}>
            <ambientLight intensity={0.6} />
            <Sky
            distance={450000} // Default
            sunPosition={[5, 1, 8]} // Where the sun is in the sky
            inclination={0} // Angle of the sun (0 = directly above)
            azimuth={0.75} // Sun’s horizontal angle
            turbidity={2} // Atmosphere thickness
            rayleigh={2} // Blueishness
            mieCoefficient={0.005} // Atmosphere dust
            mieDirectionalG={0.8} // Focus of the light
          />

            <Html
              position={[-3.5, 4.5, -5]}
              style={{
                color: "white",
                background: "rgba(0,0,0,0.5)",
                padding: "10px",
                borderRadius: "8px",
                fontFamily: "monospace",
                fontSize: "14px",
                pointerEvents: "none",
              }}
              transform
              occlude="raycast"
              zIndexRange={[1000, -100]} 
            >
              <div>
                <strong>Blobtopia</strong>
                {Object.entries(metrics).map(([k, v]) => (
                  <div key={k}>
                    {k.charAt(0).toUpperCase() + k.slice(1).replaceAll("_", " ")}: {typeof v === "number" ? `${Math.floor(v * 100)}%` : v}
                  </div>
                ))}
              </div>
            </Html>

            <ambientLight intensity={0.3} />
            <directionalLight position={[2, 5, 2]} />

            <Platform color="#32CD32" scale={[2, 1, 2]} />
            <Platform color="gray" scale={[1.2, 1, 1.2]} position={[0, 0, -3.4]} />

            <ImportedMesh
              path="models/city_merged.obj"
              mtlPath="models/city_merged.mtl"
              position={[0.4, 0.22, -3.6]}
              scale={[0.2, 0.25, 0.2]}
              rotation={[0, -Math.PI / 2, 0]}
            />
           
            <OrbitControls
              maxPolarAngle={Math.PI / 2 + Math.PI / 9}
              minPolarAngle={0}
              maxAzimuthAngle={Math.PI / 6}
              minAzimuthAngle={-Math.PI / 6}
              minDistance={5}           // don’t zoom closer than 5 units
              maxDistance={10}   
            />

            {Array.from({ length: numBlobs }).map((_, i) => (
              <Blob
                key={i}
                ref={(el) => (blobRefs.current[i] = el)}
                color={i % 2 === 0 ? "hotpink" : "cyan"}
                initialX={Math.random() * 4.0 - 2.0}
                initialY={Math.random() * 4.0 - 2.0}
                story={blobStories.get(i)}
                showStory={setStoryPopUp}
              />
            ))}
          </Canvas>
        ) : (
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "65vh" }}>
            <Button
              variant="contained"
              onClick={async () => {
                const init = await initialize();
                setInitializeDict(init);
                const m = await getWorldMetrics();
                setMetrics(m);
                setGameStarted(true);
              }}
            >
              Start Game
            </Button>
          </div>
        )}

        <HeadlineTicker headlines={Array(100).fill(headlines).flat()} />
        <SortingDropdown callback={sortBlobsByCriterion} />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-evenly", width: "50%" }}>
          <Button
            variant="outlined"
            onClick={async () => {
              iterationDance();
              const r = await wait();
              handleTimeStepDictionary(r);
            }}
          >
            Wait
          </Button>
          <h3>or</h3>
          <TextField
            label="New Policy"
            variant="outlined"
            value={policy}
            onChange={(e) => setPolicy(e.target.value)}
            style={{ width: "40vw" }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={async () => {
                      iterationDance();
                      const r = await proposePolicy(policy);
                      handleTimeStepDictionary(r);
                      setPolicy("");
                    }}
                  >
                    <HistoryEduIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </div>

        <StoryPopup open={popupOpen} onClose={() => setPopupOpen(false)} story={story} />
      </div>
    </div>
  );
}

export default App;
