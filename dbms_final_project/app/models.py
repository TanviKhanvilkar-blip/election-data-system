from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class State(Base):
    __tablename__ = "states"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)  # State code like "MH", "UP"
    region = Column(String(50))  # North, South, East, West, Northeast
    capital = Column(String(100))
    total_constituencies = Column(Integer)
    
    # Relationships
    constituencies = relationship("Constituency", back_populates="state")

class Election(Base):
    __tablename__ = "elections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # "Lok Sabha 2024", "UP Assembly 2022"
    year = Column(Integer, nullable=False)
    election_type = Column(String(50), nullable=False)  # "Lok Sabha", "Assembly"
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_constituencies = Column(Integer)
    total_candidates = Column(Integer)
    
    # Relationships
    results = relationship("Result", back_populates="election")
    voter_turnouts = relationship("VoterTurnout", back_populates="election")

class Party(Base):
    __tablename__ = "parties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    short_name = Column(String(20))  # BJP, INC, AAP
    symbol = Column(String(100))  # Lotus, Hand, Broom
    founded_year = Column(Integer)
    ideology = Column(String(100))  # Conservative, Liberal, Socialist
    national_party = Column(Boolean, default=False)
    
    # Relationships
    candidates = relationship("Candidate", back_populates="party")

class Constituency(Base):
    __tablename__ = "constituencies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20))  # PC01, AC001
    constituency_type = Column(String(20), nullable=False)  # "Lok Sabha", "Assembly"
    state_id = Column(Integer, ForeignKey("states.id"))
    reserved_for = Column(String(20), default="General")  # General, SC, ST
    
    # Relationships
    state = relationship("State", back_populates="constituencies")
    candidates = relationship("Candidate", back_populates="constituency")
    results = relationship("Result", back_populates="constituency")
    voter_turnouts = relationship("VoterTurnout", back_populates="constituency")

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))  # Male, Female, Other
    education = Column(String(200))
    occupation = Column(String(200))
    criminal_cases = Column(Integer, default=0)
    assets = Column(Float)  # in lakhs
    
    # Foreign Keys
    party_id = Column(Integer, ForeignKey("parties.id"))
    constituency_id = Column(Integer, ForeignKey("constituencies.id"))
    
    # Relationships
    party = relationship("Party", back_populates="candidates")
    constituency = relationship("Constituency", back_populates="candidates")
    results = relationship("Result", back_populates="candidate")

class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    votes_received = Column(Integer, nullable=False)
    vote_percentage = Column(Float)
    position = Column(Integer)  # 1 for winner, 2 for runner-up, etc.
    margin = Column(Integer)  # victory/defeat margin
    is_winner = Column(Boolean, default=False)
    
    # Foreign Keys
    election_id = Column(Integer, ForeignKey("elections.id"))
    constituency_id = Column(Integer, ForeignKey("constituencies.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    
    # Relationships
    election = relationship("Election", back_populates="results")
    constituency = relationship("Constituency", back_populates="results")
    candidate = relationship("Candidate", back_populates="results")

class VoterTurnout(Base):
    __tablename__ = "voter_turnout"
    
    id = Column(Integer, primary_key=True, index=True)
    total_electors = Column(Integer)
    total_votes_polled = Column(Integer)
    turnout_percentage = Column(Float)
    male_electors = Column(Integer)
    female_electors = Column(Integer)
    male_votes = Column(Integer)
    female_votes = Column(Integer)
    male_turnout_percentage = Column(Float)
    female_turnout_percentage = Column(Float)
    
    # Foreign Keys
    election_id = Column(Integer, ForeignKey("elections.id"))
    constituency_id = Column(Integer, ForeignKey("constituencies.id"))
    
    # Relationships
    election = relationship("Election", back_populates="voter_turnouts")
    constituency = relationship("Constituency", back_populates="voter_turnouts")

# User model for authentication
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
