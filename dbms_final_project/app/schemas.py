from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# Base schemas
class StateBase(BaseModel):
    name: str
    code: str
    region: Optional[str] = None
    capital: Optional[str] = None
    total_constituencies: Optional[int] = None

class StateCreate(StateBase):
    pass

class State(StateBase):
    id: int
    
    class Config:
        from_attributes = True

class PartyBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    symbol: Optional[str] = None
    founded_year: Optional[int] = None
    ideology: Optional[str] = None
    national_party: bool = False

class PartyCreate(PartyBase):
    pass

class Party(PartyBase):
    id: int
    
    class Config:
        from_attributes = True

class ElectionBase(BaseModel):
    name: str
    year: int
    election_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_constituencies: Optional[int] = None
    total_candidates: Optional[int] = None

class ElectionCreate(ElectionBase):
    pass

class Election(ElectionBase):
    id: int
    
    class Config:
        from_attributes = True

class ConstituencyBase(BaseModel):
    name: str
    code: Optional[str] = None
    constituency_type: str
    state_id: int
    reserved_for: str = "General"

class ConstituencyCreate(ConstituencyBase):
    pass

class Constituency(ConstituencyBase):
    id: int
    state: Optional[State] = None
    
    class Config:
        from_attributes = True

class CandidateBase(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    criminal_cases: int = 0
    assets: Optional[float] = None
    party_id: int
    constituency_id: int

class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: int
    party: Optional[Party] = None
    constituency: Optional[Constituency] = None
    
    class Config:
        from_attributes = True

class ResultBase(BaseModel):
    votes_received: int
    vote_percentage: Optional[float] = None
    position: Optional[int] = None
    margin: Optional[int] = None
    is_winner: bool = False
    election_id: int
    constituency_id: int
    candidate_id: int

class ResultCreate(ResultBase):
    pass

class Result(ResultBase):
    id: int
    election: Optional[Election] = None
    constituency: Optional[Constituency] = None
    candidate: Optional[Candidate] = None
    
    class Config:
        from_attributes = True

class VoterTurnoutBase(BaseModel):
    total_electors: int
    total_votes_polled: int
    turnout_percentage: Optional[float] = None
    male_electors: Optional[int] = None
    female_electors: Optional[int] = None
    male_votes: Optional[int] = None
    female_votes: Optional[int] = None
    male_turnout_percentage: Optional[float] = None
    female_turnout_percentage: Optional[float] = None
    election_id: int
    constituency_id: int

class VoterTurnoutCreate(VoterTurnoutBase):
    pass

class VoterTurnout(VoterTurnoutBase):
    id: int
    election: Optional[Election] = None
    constituency: Optional[Constituency] = None
    
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Dashboard specific schemas
class PartySeatsData(BaseModel):
    party_name: str
    party_short_name: str
    seats_won: int
    total_votes: int
    vote_percentage: float

class StateWiseResults(BaseModel):
    state_name: str
    total_seats: int
    leading_party: str
    turnout_percentage: float

class ClosestContests(BaseModel):
    constituency_name: str
    state_name: str
    winner_name: str
    winner_party: str
    margin: int
    margin_percentage: float

class TurnoutAnalysis(BaseModel):
    state_name: str
    constituency_name: str
    total_turnout: float
    male_turnout: float
    female_turnout: float
    gender_gap: float

# --- National overview / KPI panel -----------------------------------------
class ElectionOverview(BaseModel):
    total_seats: int
    total_constituencies_reporting: int
    total_candidates: int
    total_votes_cast: int
    overall_turnout_percentage: float
    nota_votes: int
    nota_percentage: float
    women_candidates: int
    women_winners: int
    women_candidate_share: float
    women_winner_share: float
    candidates_with_criminal_cases: int
    criminal_case_share: float
    winners_with_criminal_cases: int
    winner_criminal_case_share: float
    avg_candidate_age: float
    median_winner_assets_lakhs: float
    winners_crorepati_share: float
    independents_won: int

# --- Gender representation by party ----------------------------------------
class GenderRepresentationByParty(BaseModel):
    party_short_name: str
    total_contested: int
    total_won: int
    women_contested: int
    women_won: int
    women_candidate_share: float

# --- Education profile of winners -------------------------------------------
class EducationBreakdown(BaseModel):
    education: str
    winners: int
    share: float

# --- Candidate wealth ---------------------------------------------------
class WealthLeader(BaseModel):
    candidate_name: str
    party_short_name: str
    state_name: str
    constituency_name: str
    assets_lakhs: float
    is_winner: bool

# --- Criminal-cases profile by party -----------------------------------
class CriminalCasesByParty(BaseModel):
    party_short_name: str
    total_candidates: int
    candidates_with_cases: int
    share_with_cases: float

# --- Constituency lookup ------------------------------------------------
class ConstituencyCandidateResult(BaseModel):
    candidate_name: str
    party_short_name: str
    party_name: str
    votes_received: int
    vote_percentage: float
    is_winner: bool
    gender: Optional[str] = None
    age: Optional[int] = None
    education: Optional[str] = None
    criminal_cases: Optional[int] = None
    assets_lakhs: Optional[float] = None

class ConstituencyLookup(BaseModel):
    constituency_name: str
    state_name: str
    reserved_for: str
    total_electors: Optional[int] = None
    total_votes_polled: Optional[int] = None
    turnout_percentage: Optional[float] = None
    results: List[ConstituencyCandidateResult]

class ConstituencySearchResult(BaseModel):
    constituency_name: str
    state_name: str
    winner_name: Optional[str] = None
    winner_party: Optional[str] = None
