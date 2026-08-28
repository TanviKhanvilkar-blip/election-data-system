from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
import os

from app import crud, models, schemas, auth
from app.database import SessionLocal, engine, get_db, create_tables

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Election Data Management System",
    description="A comprehensive system for managing Indian election data with analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize database and create default user."""
    create_tables()
    db = SessionLocal()
    try:
        auth.create_default_user(db)
    finally:
        db.close()

# Authentication Routes
@app.post("/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    return crud.create_user(db=db, user=user)

@app.post("/auth/login", response_model=schemas.Token)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = auth.authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.User)
async def read_current_user(current_user: models.User = Depends(auth.get_current_active_user)):
    """Get current user information."""
    return current_user

# States Routes
@app.get("/states/", response_model=List[schemas.State])
def read_states(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all states."""
    return crud.get_states(db, skip=skip, limit=limit)

@app.post("/states/", response_model=schemas.State)
def create_state(
    state: schemas.StateCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new state."""
    existing_state = crud.get_state_by_code(db, state.code)
    if existing_state:
        raise HTTPException(status_code=400, detail="State code already exists")
    return crud.create_state(db=db, state=state)

@app.get("/states/{state_id}", response_model=schemas.State)
def read_state(
    state_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get a specific state."""
    state = crud.get_state(db, state_id=state_id)
    if state is None:
        raise HTTPException(status_code=404, detail="State not found")
    return state

@app.put("/states/{state_id}", response_model=schemas.State)
def update_state(
    state_id: int, 
    state: schemas.StateCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update a state."""
    updated_state = crud.update_state(db, state_id=state_id, state=state)
    if updated_state is None:
        raise HTTPException(status_code=404, detail="State not found")
    return updated_state

@app.delete("/states/{state_id}")
def delete_state(
    state_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete a state."""
    if not crud.delete_state(db, state_id=state_id):
        raise HTTPException(status_code=404, detail="State not found")
    return {"message": "State deleted successfully"}

# Parties Routes
@app.get("/parties/", response_model=List[schemas.Party])
def read_parties(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all parties."""
    return crud.get_parties(db, skip=skip, limit=limit)

@app.post("/parties/", response_model=schemas.Party)
def create_party(
    party: schemas.PartyCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new party."""
    return crud.create_party(db=db, party=party)

@app.get("/parties/{party_id}", response_model=schemas.Party)
def read_party(
    party_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get a specific party."""
    party = crud.get_party(db, party_id=party_id)
    if party is None:
        raise HTTPException(status_code=404, detail="Party not found")
    return party

@app.put("/parties/{party_id}", response_model=schemas.Party)
def update_party(
    party_id: int, 
    party: schemas.PartyCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update a party."""
    updated_party = crud.update_party(db, party_id=party_id, party=party)
    if updated_party is None:
        raise HTTPException(status_code=404, detail="Party not found")
    return updated_party

@app.delete("/parties/{party_id}")
def delete_party(
    party_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete a party."""
    if not crud.delete_party(db, party_id=party_id):
        raise HTTPException(status_code=404, detail="Party not found")
    return {"message": "Party deleted successfully"}

# Elections Routes
@app.get("/elections/", response_model=List[schemas.Election])
def read_elections(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all elections."""
    return crud.get_elections(db, skip=skip, limit=limit)

@app.post("/elections/", response_model=schemas.Election)
def create_election(
    election: schemas.ElectionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new election."""
    return crud.create_election(db=db, election=election)

@app.get("/elections/{election_id}", response_model=schemas.Election)
def read_election(
    election_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get a specific election."""
    election = crud.get_election(db, election_id=election_id)
    if election is None:
        raise HTTPException(status_code=404, detail="Election not found")
    return election

@app.put("/elections/{election_id}", response_model=schemas.Election)
def update_election(
    election_id: int, 
    election: schemas.ElectionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update an election."""
    updated_election = crud.update_election(db, election_id=election_id, election=election)
    if updated_election is None:
        raise HTTPException(status_code=404, detail="Election not found")
    return updated_election

@app.delete("/elections/{election_id}")
def delete_election(
    election_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete an election."""
    if not crud.delete_election(db, election_id=election_id):
        raise HTTPException(status_code=404, detail="Election not found")
    return {"message": "Election deleted successfully"}

# Constituencies Routes
@app.get("/constituencies/", response_model=List[schemas.Constituency])
def read_constituencies(
    skip: int = 0, 
    limit: int = 100, 
    state_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all constituencies."""
    return crud.get_constituencies(db, skip=skip, limit=limit, state_id=state_id)

@app.post("/constituencies/", response_model=schemas.Constituency)
def create_constituency(
    constituency: schemas.ConstituencyCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new constituency."""
    return crud.create_constituency(db=db, constituency=constituency)

@app.get("/constituencies/{constituency_id}", response_model=schemas.Constituency)
def read_constituency(
    constituency_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get a specific constituency."""
    constituency = crud.get_constituency(db, constituency_id=constituency_id)
    if constituency is None:
        raise HTTPException(status_code=404, detail="Constituency not found")
    return constituency

@app.put("/constituencies/{constituency_id}", response_model=schemas.Constituency)
def update_constituency(
    constituency_id: int, 
    constituency: schemas.ConstituencyCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update a constituency."""
    updated_constituency = crud.update_constituency(db, constituency_id=constituency_id, constituency=constituency)
    if updated_constituency is None:
        raise HTTPException(status_code=404, detail="Constituency not found")
    return updated_constituency

@app.delete("/constituencies/{constituency_id}")
def delete_constituency(
    constituency_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete a constituency."""
    if not crud.delete_constituency(db, constituency_id=constituency_id):
        raise HTTPException(status_code=404, detail="Constituency not found")
    return {"message": "Constituency deleted successfully"}

# Candidates Routes
@app.get("/candidates/", response_model=List[schemas.Candidate])
def read_candidates(
    skip: int = 0, 
    limit: int = 100, 
    party_id: Optional[int] = None,
    constituency_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all candidates."""
    return crud.get_candidates(db, skip=skip, limit=limit, party_id=party_id, constituency_id=constituency_id)

@app.post("/candidates/", response_model=schemas.Candidate)
def create_candidate(
    candidate: schemas.CandidateCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new candidate."""
    return crud.create_candidate(db=db, candidate=candidate)

@app.get("/candidates/{candidate_id}", response_model=schemas.Candidate)
def read_candidate(
    candidate_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get a specific candidate."""
    candidate = crud.get_candidate(db, candidate_id=candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@app.put("/candidates/{candidate_id}", response_model=schemas.Candidate)
def update_candidate(
    candidate_id: int, 
    candidate: schemas.CandidateCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update a candidate."""
    updated_candidate = crud.update_candidate(db, candidate_id=candidate_id, candidate=candidate)
    if updated_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return updated_candidate

@app.delete("/candidates/{candidate_id}")
def delete_candidate(
    candidate_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete a candidate."""
    if not crud.delete_candidate(db, candidate_id=candidate_id):
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"message": "Candidate deleted successfully"}

# Results Routes
@app.get("/results/", response_model=List[schemas.Result])
def read_results(
    skip: int = 0, 
    limit: int = 100, 
    election_id: Optional[int] = None,
    constituency_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all results."""
    return crud.get_results(db, skip=skip, limit=limit, election_id=election_id, constituency_id=constituency_id)

@app.post("/results/", response_model=schemas.Result)
def create_result(
    result: schemas.ResultCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create a new result."""
    return crud.create_result(db=db, result=result)

@app.get("/results/{result_id}", response_model=schemas.Result)
def read_result(
    result_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get a specific result."""
    result = crud.get_result(db, result_id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return result

@app.put("/results/{result_id}", response_model=schemas.Result)
def update_result(
    result_id: int, 
    result: schemas.ResultCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update a result."""
    updated_result = crud.update_result(db, result_id=result_id, result=result)
    if updated_result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return updated_result

@app.delete("/results/{result_id}")
def delete_result(
    result_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete a result."""
    if not crud.delete_result(db, result_id=result_id):
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Result deleted successfully"}

# Voter Turnout Routes
@app.get("/turnout/", response_model=List[schemas.VoterTurnout])
def read_turnout(
    skip: int = 0, 
    limit: int = 100, 
    election_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get all voter turnout data."""
    return crud.get_voter_turnout(db, skip=skip, limit=limit, election_id=election_id)

@app.post("/turnout/", response_model=schemas.VoterTurnout)
def create_turnout(
    turnout: schemas.VoterTurnoutCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Create new voter turnout data."""
    return crud.create_turnout(db=db, turnout=turnout)

@app.get("/turnout/{turnout_id}", response_model=schemas.VoterTurnout)
def read_single_turnout(
    turnout_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get specific voter turnout data."""
    turnout = crud.get_turnout(db, turnout_id=turnout_id)
    if turnout is None:
        raise HTTPException(status_code=404, detail="Turnout data not found")
    return turnout

@app.put("/turnout/{turnout_id}", response_model=schemas.VoterTurnout)
def update_turnout(
    turnout_id: int, 
    turnout: schemas.VoterTurnoutCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update voter turnout data."""
    updated_turnout = crud.update_turnout(db, turnout_id=turnout_id, turnout=turnout)
    if updated_turnout is None:
        raise HTTPException(status_code=404, detail="Turnout data not found")
    return updated_turnout

@app.delete("/turnout/{turnout_id}")
def delete_turnout(
    turnout_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete voter turnout data."""
    if not crud.delete_turnout(db, turnout_id=turnout_id):
        raise HTTPException(status_code=404, detail="Turnout data not found")
    return {"message": "Turnout data deleted successfully"}

# Dashboard Analytics Routes
@app.get("/analytics/party-seats/{election_id}", response_model=List[schemas.PartySeatsData])
def get_party_seats_analysis(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get party-wise seat count and vote share analysis."""
    return crud.get_party_wise_seats(db, election_id=election_id)

@app.get("/analytics/state-results/{election_id}", response_model=List[schemas.StateWiseResults])
def get_state_results_analysis(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get state-wise election results summary."""
    return crud.get_state_wise_results(db, election_id=election_id)

@app.get("/analytics/closest-contests/{election_id}", response_model=List[schemas.ClosestContests])
def get_closest_contests_analysis(
    election_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get closest contests by victory margin."""
    return crud.get_closest_contests(db, election_id=election_id, limit=limit)

@app.get("/analytics/turnout-analysis/{election_id}", response_model=List[schemas.TurnoutAnalysis])
def get_turnout_analysis(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get gender-wise turnout analysis."""
    return crud.get_turnout_analysis(db, election_id=election_id)

@app.get("/analytics/overview/{election_id}", response_model=schemas.ElectionOverview)
def get_election_overview(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """National-level KPI summary: turnout, NOTA share, women's representation,
    candidates with criminal cases, wealth, and more."""
    return crud.get_election_overview(db, election_id=election_id)

@app.get("/analytics/landslide-contests/{election_id}", response_model=List[schemas.ClosestContests])
def get_landslide_contests_analysis(
    election_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get the safest seats (largest winning margins)."""
    return crud.get_landslide_contests(db, election_id=election_id, limit=limit)

@app.get("/analytics/gender-representation/{election_id}", response_model=List[schemas.GenderRepresentationByParty])
def get_gender_representation_analysis(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Women candidates fielded vs. elected, by party."""
    return crud.get_gender_representation(db, election_id=election_id)

@app.get("/analytics/education-breakdown/{election_id}", response_model=List[schemas.EducationBreakdown])
def get_education_breakdown_analysis(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Education profile of winning candidates."""
    return crud.get_education_breakdown(db, election_id=election_id)

@app.get("/analytics/wealth-leaders/{election_id}", response_model=List[schemas.WealthLeader])
def get_wealth_leaders_analysis(
    election_id: int,
    limit: int = 10,
    winners_only: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Wealthiest candidates by declared assets."""
    return crud.get_wealth_leaders(db, election_id=election_id, limit=limit, winners_only=winners_only)

@app.get("/analytics/criminal-cases-by-party/{election_id}", response_model=List[schemas.CriminalCasesByParty])
def get_criminal_cases_by_party_analysis(
    election_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Share of candidates with declared criminal cases, by party."""
    return crud.get_criminal_cases_by_party(db, election_id=election_id)

@app.get("/analytics/constituency-search/{election_id}", response_model=List[schemas.ConstituencySearchResult])
def search_constituencies(
    election_id: int,
    q: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Search constituencies by name for the lookup box."""
    if len(q.strip()) < 2:
        return []
    return crud.search_constituencies(db, election_id=election_id, query=q)

@app.get("/analytics/constituency/{election_id}/{constituency_name}", response_model=schemas.ConstituencyLookup)
def get_constituency_lookup(
    election_id: int,
    constituency_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Full candidate-by-candidate breakdown for one constituency."""
    lookup = crud.get_constituency_lookup(db, election_id=election_id, constituency_name=constituency_name)
    if not lookup:
        raise HTTPException(status_code=404, detail="Constituency not found")
    return lookup

# Root route to serve the dashboard
@app.get("/", response_class=HTMLResponse)
async def read_dashboard():
    """Serve the main dashboard."""
    try:
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Election Data Management System</h1><p>Dashboard will be available soon!</p><p><a href='/docs'>API Documentation</a></p>", status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
