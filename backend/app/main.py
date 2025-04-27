from fastapi import FastAPI, HTTPException, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from app.blob_sim import EnhancedGameState  # Using the correct class from your paste.txt

# Pydantic models for request/response data
class InitializeRequest(BaseModel):
    num_blobs: int = Field(..., description="Number of blobs to initialize", gt=0)
    num_societies: int = Field(3, description="Number of societies to create")
    
    # Add validator to prevent resource exhaustion
    @validator('num_blobs')
    def check_reasonable_blobs(cls, v):
        if v > 50:  # Prevent creating too many blobs
            raise ValueError("Maximum number of blobs is 50")
        return v

class PolicyRequest(BaseModel):
    proposal: str = Field(..., description="Policy proposal text")
    temperature: float = Field(0.7, description="Temperature for generation", ge=0.0, le=1.0)

class BlobResponse(BaseModel):
    blob_id: int
    name: str
    society_id: Optional[int]
    personality: str
    traits: List[str]
    properties: Dict[str, Any]
    image_url: Optional[str]
    history: Optional[List[Dict[str, Any]]] = None

class SocietyResponse(BaseModel):
    society_id: int
    ideology: str
    values: List[str]
    members: List[int]
    image_url: Optional[str]

class EventResponse(BaseModel):
    year: int
    headline: str
    subheadlines: List[str]
    headline_metric: str
    details: str
    impacts: Dict[str, str]
    image_url: Optional[str]

class StatusResponse(BaseModel):
    current_year: int
    num_blobs: int
    num_societies: int
    num_events: int
    status_report: str

# Initialize FastAPI app
app = FastAPI(
    title="Blob Simulation API",
    description="API for managing a political evolution game with blob creatures",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the game state
game_state = EnhancedGameState()

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Blob Simulation API is running",
        "version": "1.0.0",
        "endpoints": [
            "/initialize", "/run_iteration", "/status", "/propose_policy",
            "/blobs", "/societies", "/events", 
            "/blob/{blob_id}", "/society/{society_id}", "/event/{event_index}"
        ]
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "initialized": len(game_state.blobs) > 0}

@app.post("/initialize", tags=["Simulation Control"], response_model=Dict[str, Any])
async def initialize(request: InitializeRequest):
    """
    Initialize the simulation with a specified number of blobs and societies.
    Returns basic information about the generated world.
    """
    try:
        game_state.initialize_with_personalities(
            num_blobs=request.num_blobs,
            num_societies=request.num_societies
        )
        
        return {
            "status": "Game initialized successfully",
            "num_blobs": len(game_state.blobs),
            "num_societies": len(game_state.societies),
            "current_year": game_state.current_year,
            "blobs": [{"id": b.blob_id, "name": b.name} for b in game_state.blobs],
            "societies": [{"id": s.society_id, "ideology": s.ideology} for s in game_state.societies]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize game: {str(e)}")

@app.get("/run_iteration", tags=["Simulation Control"], response_model=Dict[str, Any])
async def run_iteration(temperature: float = Query(0.7, ge=0.0, le=1.0), create_image: bool = Query(True)):
    """
    Run a single iteration of the simulation.
    Returns information about the generated event.
    """
    if not game_state.blobs:
        raise HTTPException(status_code=400, detail="Game not initialized. Call /initialize first.")
    
    try:
        event = game_state.run_iteration(temperature=temperature, create_image=create_image)
        
        if not event:
            raise HTTPException(status_code=500, detail="Failed to generate a valid event")
        
        # Get the current metrics
        metrics = game_state.get_metrics()

        hacked_impact_string_dict = {}
        #loop over all blobs
        for blob in game_state.blobs:
            blob_id = blob.blob_id
            temp_str = blob.personality + "\nHistory of Impacts:\n"
            #now add the history to the string
            if blob.history:
                for history in blob.history:
                    temp_str += f"Iteration - {history['year']}: {history['description']}\n"
            else:
                temp_str += "No history available for this blob.\n"
            hacked_impact_string_dict[blob_id] = temp_str
        
        return {
            "status": "Iteration completed",
            "current_year": game_state.current_year,
            "metrics": metrics,  # Include world metrics
            "event": {
                "year": event.year,
                "headline": event.headline,
                "subheadlines": event.subheadlines,
                "headline_metrics": event.metrics_headline,
                "details": event.details,
                "impacts": hacked_impact_string_dict,
                "image_url": event.image_url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run iteration: {str(e)}")

@app.get("/world_metrics", tags=["Information"], response_model=Dict[str, Any])
async def get_world_metrics():
    """Get the current world metrics."""
    if not game_state.blobs:
        raise HTTPException(status_code=400, detail="Game not initialized. Call /initialize first.")
    
    try:
        metrics = game_state.get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get world metrics: {str(e)}")

@app.post("/propose_policy", tags=["Simulation Control"], response_model=Dict[str, Any])
async def propose_policy(request: PolicyRequest):
    """
    Submit a policy proposition to the simulation.
    Returns the result and effect on the world.
    """
    if not game_state.blobs:
        raise HTTPException(status_code=400, detail="Game not initialized. Call /initialize first.")
    
    try:
        result = game_state.policy_proposition(
            proposal=request.proposal,
            temperature=request.temperature,
            create_image=False
        )
        
        # Get current metrics
        metrics = game_state.get_metrics()

        hacked_impact_string_dict = {}
        #loop over all blobs
        for blob in game_state.blobs:
            blob_id = blob.blob_id
            temp_str = blob.personality + "\nHistory of Impacts:\n"
            #now add the history to the string
            if blob.history:
                for history in blob.history:
                    temp_str += f"Iteration - {history['year']}: {history['description']}\n"
            else:
                temp_str += "No history available for this blob.\n"
            hacked_impact_string_dict[blob_id] = temp_str
        
        # Get the most recent event (should be the one created by the policy)
        if game_state.world_events:
            event = game_state.world_events[-1]
            event_data = {
                "year": event.year,
                "headline": event.headline,
                "subheadlines": event.subheadlines,
                "headline_metrics": event.metrics_headline,
                "details": event.details,
                "impacts": hacked_impact_string_dict,
                "image_url": event.image_url
            }
        else:
            event_data = None
        
        return {
            "status": "Policy proposition processed",
            #"result": result,
            "current_year": game_state.current_year,
            "metrics": metrics,  # Include world metrics
            "event": event_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process policy: {str(e)}")

@app.get("/status", tags=["Information"], response_model=StatusResponse)
async def get_status():
    """Get the current status report of the world."""
    if not game_state.blobs:
        raise HTTPException(status_code=400, detail="Game not initialized. Call /initialize first.")
    
    try:
        status_report = game_state.get_world_status_report()
        
        return StatusResponse(
            current_year=game_state.current_year,
            num_blobs=len(game_state.blobs),
            num_societies=len(game_state.societies),
            num_events=len(game_state.world_events),
            status_report=status_report
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.get("/blobs", tags=["Information"], response_model=List[BlobResponse])
async def get_blobs():
    """Get information about all blobs in the simulation."""
    if not game_state.blobs:
        raise HTTPException(status_code=400, detail="Game not initialized. Call /initialize first.")
    
    return [
        BlobResponse(
            blob_id=blob.blob_id,
            name=blob.name,
            society_id=blob.society_id,
            personality=blob.personality,
            traits=blob.traits,
            properties=blob.properties,
            image_url=blob.image_url,
            history = blob.history
        )
        for blob in game_state.blobs
    ]

@app.get("/societies", tags=["Information"], response_model=List[SocietyResponse])
async def get_societies():
    """Get information about all societies in the simulation."""
    if not game_state.societies:
        raise HTTPException(status_code=400, detail="No societies found. Initialize the game first.")
    
    return [
        SocietyResponse(
            society_id=society.society_id,
            ideology=society.ideology,
            values=society.values,
            members=society.members,
            image_url=society.image_url
        )
        for society in game_state.societies
    ]

@app.get("/events", tags=["Information"], response_model=List[EventResponse])
async def get_events():
    """Get a list of all world events that have occurred."""
    if not game_state.world_events:
        raise HTTPException(status_code=400, detail="No events found. Run iterations first.")
    
    return [
        EventResponse(
            year=event.year,
            headline=event.headline,
            headline_metric=event.metrics_headline,
            details=event.details,
            impacts={str(blob_id): impact for blob_id, impact in event.impacts.items()},
            image_url=event.image_url
        )
        for event in game_state.world_events
    ]

@app.get("/blob/{blob_id}", tags=["Information"], response_model=Dict[str, Any])
async def get_blob(blob_id: int = Path(..., description="The ID of the blob to retrieve")):
    """Get detailed information about a specific blob, including relationships."""
    if not game_state.blobs:
        raise HTTPException(status_code=400, detail="Game not initialized. Call /initialize first.")
    
    blob = next((b for b in game_state.blobs if b.blob_id == blob_id), None)
    if not blob:
        raise HTTPException(status_code=404, detail=f"Blob with ID {blob_id} not found")
    
    # Get the society if the blob is part of one
    society = None
    if blob.society_id is not None:
        society = next((s for s in game_state.societies if s.society_id == blob.society_id), None)
    
    # Format relationships
    relationships = []
    for other_id, score in blob.relationships.items():
        other_blob = next((b for b in game_state.blobs if b.blob_id == other_id), None)
        if other_blob:
            relationships.append({
                "blob_id": other_id,
                "name": other_blob.name,
                "score": score,
                "status": get_relationship_status(score)
            })
    
    # Format history
    history_events = []
    for event in blob.history:
        history_events.append({
            "year": event.get("year"),
            "type": event.get("type"),
            "description": event.get("description")
        })
    
    return {
        "blob_id": blob.blob_id,
        "name": blob.name,
        "society": {
            "society_id": society.society_id,
            "ideology": society.ideology,
            "values": society.values
        } if society else None,
        "personality": blob.personality,
        "traits": blob.traits,
        "properties": blob.properties,
        "image_url": blob.image_url,
        "relationships": relationships,
        "history": history_events
    }

@app.get("/society/{society_id}", tags=["Information"], response_model=Dict[str, Any])
async def get_society(society_id: int = Path(..., description="The ID of the society to retrieve")):
    """Get detailed information about a specific society, including all members."""
    if not game_state.societies:
        raise HTTPException(status_code=400, detail="No societies found. Initialize the game first.")
    
    society = next((s for s in game_state.societies if s.society_id == society_id), None)
    if not society:
        raise HTTPException(status_code=404, detail=f"Society with ID {society_id} not found")
    
    # Get all members of this society
    members = []
    for blob in game_state.blobs:
        if blob.society_id == society_id:
            members.append({
                "blob_id": blob.blob_id,
                "name": blob.name,
                "personality": blob.personality,
                "traits": blob.traits,
                "image_url": blob.image_url
            })
    
    # Get relations with other societies
    relations = []
    for other_id, score in society.relations.items():
        other_society = next((s for s in game_state.societies if s.society_id == other_id), None)
        if other_society:
            relations.append({
                "society_id": other_id,
                "ideology": other_society.ideology,
                "score": score,
                "status": get_relationship_status(score)
            })
    
    return {
        "society_id": society.society_id,
        "ideology": society.ideology,
        "values": society.values,
        "image_url": society.image_url,
        "members": members,
        "relations": relations
    }

@app.get("/event/{event_index}", tags=["Information"], response_model=Dict[str, Any])
async def get_event(event_index: int = Path(..., description="The index of the event to retrieve")):
    """Get detailed information about a specific event by its index in the event history."""
    if not game_state.world_events:
        raise HTTPException(status_code=400, detail="No events found. Run iterations first.")
    
    if event_index < 0 or event_index >= len(game_state.world_events):
        raise HTTPException(status_code=404, detail=f"Event at index {event_index} not found")
    
    event = game_state.world_events[event_index]
    
    # Format impacts with blob names
    impacts_with_names = {}
    for blob_id, impact in event.impacts.items():
        try:
            blob_id_int = int(blob_id)
            blob = next((b for b in game_state.blobs if b.blob_id == blob_id_int), None)
            if blob:
                impacts_with_names[f"{blob.name} (ID: {blob_id})"] = impact
            else:
                impacts_with_names[f"Blob ID: {blob_id}"] = impact
        except (ValueError, TypeError):
            # If blob_id can't be converted to int, just use it as is
            impacts_with_names[str(blob_id)] = impact
    
    return {
        "index": event_index,
        "year": event.year,
        "headline": event.headline,
        "details": event.details,
        "impacts": impacts_with_names,
        "image_url": event.image_url,
        "society_relations": event.society_relations if hasattr(event, 'society_relations') else {}
    }

@app.get("/relations", tags=["Information"])
async def get_society_relations():
    """Get a comprehensive report of relations between societies."""
    if not game_state.societies:
        raise HTTPException(status_code=400, detail="No societies found. Initialize the game first.")
    
    return {"relations_report": game_state.get_society_relations_report()}

# Helper function to convert relationship scores to status text
def get_relationship_status(score: float) -> str:
    """Convert a relationship score to a descriptive status."""
    if score > 0.7:
        return "close friend"
    elif score > 0.3:
        return "friend"
    elif score > -0.3:
        return "acquaintance"
    elif score > -0.7:
        return "dislikes"
    else:
        return "enemy"

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)