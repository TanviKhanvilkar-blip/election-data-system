from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import statistics
from . import models, schemas
from .auth import get_password_hash

# States CRUD
def get_states(db: Session, skip: int = 0, limit: int = 100) -> List[models.State]:
    return db.query(models.State).offset(skip).limit(limit).all()

def get_state(db: Session, state_id: int) -> Optional[models.State]:
    return db.query(models.State).filter(models.State.id == state_id).first()

def get_state_by_code(db: Session, code: str) -> Optional[models.State]:
    return db.query(models.State).filter(models.State.code == code).first()

def create_state(db: Session, state: schemas.StateCreate) -> models.State:
    db_state = models.State(**state.dict())
    db.add(db_state)
    db.commit()
    db.refresh(db_state)
    return db_state

def update_state(db: Session, state_id: int, state: schemas.StateCreate) -> Optional[models.State]:
    db_state = db.query(models.State).filter(models.State.id == state_id).first()
    if db_state:
        for key, value in state.dict().items():
            setattr(db_state, key, value)
        db.commit()
        db.refresh(db_state)
    return db_state

def delete_state(db: Session, state_id: int) -> bool:
    db_state = db.query(models.State).filter(models.State.id == state_id).first()
    if db_state:
        db.delete(db_state)
        db.commit()
        return True
    return False

# Parties CRUD
def get_parties(db: Session, skip: int = 0, limit: int = 100) -> List[models.Party]:
    return db.query(models.Party).offset(skip).limit(limit).all()

def get_party(db: Session, party_id: int) -> Optional[models.Party]:
    return db.query(models.Party).filter(models.Party.id == party_id).first()

def create_party(db: Session, party: schemas.PartyCreate) -> models.Party:
    db_party = models.Party(**party.dict())
    db.add(db_party)
    db.commit()
    db.refresh(db_party)
    return db_party

def update_party(db: Session, party_id: int, party: schemas.PartyCreate) -> Optional[models.Party]:
    db_party = db.query(models.Party).filter(models.Party.id == party_id).first()
    if db_party:
        for key, value in party.dict().items():
            setattr(db_party, key, value)
        db.commit()
        db.refresh(db_party)
    return db_party

def delete_party(db: Session, party_id: int) -> bool:
    db_party = db.query(models.Party).filter(models.Party.id == party_id).first()
    if db_party:
        db.delete(db_party)
        db.commit()
        return True
    return False

# Elections CRUD
def get_elections(db: Session, skip: int = 0, limit: int = 100) -> List[models.Election]:
    return db.query(models.Election).offset(skip).limit(limit).all()

def get_election(db: Session, election_id: int) -> Optional[models.Election]:
    return db.query(models.Election).filter(models.Election.id == election_id).first()

def create_election(db: Session, election: schemas.ElectionCreate) -> models.Election:
    db_election = models.Election(**election.dict())
    db.add(db_election)
    db.commit()
    db.refresh(db_election)
    return db_election

def update_election(db: Session, election_id: int, election: schemas.ElectionCreate) -> Optional[models.Election]:
    db_election = db.query(models.Election).filter(models.Election.id == election_id).first()
    if db_election:
        for key, value in election.dict().items():
            setattr(db_election, key, value)
        db.commit()
        db.refresh(db_election)
    return db_election

def delete_election(db: Session, election_id: int) -> bool:
    db_election = db.query(models.Election).filter(models.Election.id == election_id).first()
    if db_election:
        db.delete(db_election)
        db.commit()
        return True
    return False

# Constituencies CRUD
def get_constituencies(db: Session, skip: int = 0, limit: int = 100, state_id: Optional[int] = None) -> List[models.Constituency]:
    query = db.query(models.Constituency)
    if state_id:
        query = query.filter(models.Constituency.state_id == state_id)
    return query.offset(skip).limit(limit).all()

def get_constituency(db: Session, constituency_id: int) -> Optional[models.Constituency]:
    return db.query(models.Constituency).filter(models.Constituency.id == constituency_id).first()

def create_constituency(db: Session, constituency: schemas.ConstituencyCreate) -> models.Constituency:
    db_constituency = models.Constituency(**constituency.dict())
    db.add(db_constituency)
    db.commit()
    db.refresh(db_constituency)
    return db_constituency

def update_constituency(db: Session, constituency_id: int, constituency: schemas.ConstituencyCreate) -> Optional[models.Constituency]:
    db_constituency = db.query(models.Constituency).filter(models.Constituency.id == constituency_id).first()
    if db_constituency:
        for key, value in constituency.dict().items():
            setattr(db_constituency, key, value)
        db.commit()
        db.refresh(db_constituency)
    return db_constituency

def delete_constituency(db: Session, constituency_id: int) -> bool:
    db_constituency = db.query(models.Constituency).filter(models.Constituency.id == constituency_id).first()
    if db_constituency:
        db.delete(db_constituency)
        db.commit()
        return True
    return False

# Candidates CRUD
def get_candidates(db: Session, skip: int = 0, limit: int = 100, party_id: Optional[int] = None, constituency_id: Optional[int] = None) -> List[models.Candidate]:
    query = db.query(models.Candidate)
    if party_id:
        query = query.filter(models.Candidate.party_id == party_id)
    if constituency_id:
        query = query.filter(models.Candidate.constituency_id == constituency_id)
    return query.offset(skip).limit(limit).all()

def get_candidate(db: Session, candidate_id: int) -> Optional[models.Candidate]:
    return db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()

def create_candidate(db: Session, candidate: schemas.CandidateCreate) -> models.Candidate:
    db_candidate = models.Candidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def update_candidate(db: Session, candidate_id: int, candidate: schemas.CandidateCreate) -> Optional[models.Candidate]:
    db_candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if db_candidate:
        for key, value in candidate.dict().items():
            setattr(db_candidate, key, value)
        db.commit()
        db.refresh(db_candidate)
    return db_candidate

def delete_candidate(db: Session, candidate_id: int) -> bool:
    db_candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if db_candidate:
        db.delete(db_candidate)
        db.commit()
        return True
    return False

# Results CRUD
def get_results(db: Session, skip: int = 0, limit: int = 100, election_id: Optional[int] = None, constituency_id: Optional[int] = None) -> List[models.Result]:
    query = db.query(models.Result)
    if election_id:
        query = query.filter(models.Result.election_id == election_id)
    if constituency_id:
        query = query.filter(models.Result.constituency_id == constituency_id)
    return query.offset(skip).limit(limit).all()

def get_result(db: Session, result_id: int) -> Optional[models.Result]:
    return db.query(models.Result).filter(models.Result.id == result_id).first()

def create_result(db: Session, result: schemas.ResultCreate) -> models.Result:
    db_result = models.Result(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def update_result(db: Session, result_id: int, result: schemas.ResultCreate) -> Optional[models.Result]:
    db_result = db.query(models.Result).filter(models.Result.id == result_id).first()
    if db_result:
        for key, value in result.dict().items():
            setattr(db_result, key, value)
        db.commit()
        db.refresh(db_result)
    return db_result

def delete_result(db: Session, result_id: int) -> bool:
    db_result = db.query(models.Result).filter(models.Result.id == result_id).first()
    if db_result:
        db.delete(db_result)
        db.commit()
        return True
    return False

# Voter Turnout CRUD
def get_voter_turnout(db: Session, skip: int = 0, limit: int = 100, election_id: Optional[int] = None) -> List[models.VoterTurnout]:
    query = db.query(models.VoterTurnout)
    if election_id:
        query = query.filter(models.VoterTurnout.election_id == election_id)
    return query.offset(skip).limit(limit).all()

def get_turnout(db: Session, turnout_id: int) -> Optional[models.VoterTurnout]:
    return db.query(models.VoterTurnout).filter(models.VoterTurnout.id == turnout_id).first()

def create_turnout(db: Session, turnout: schemas.VoterTurnoutCreate) -> models.VoterTurnout:
    db_turnout = models.VoterTurnout(**turnout.dict())
    db.add(db_turnout)
    db.commit()
    db.refresh(db_turnout)
    return db_turnout

def update_turnout(db: Session, turnout_id: int, turnout: schemas.VoterTurnoutCreate) -> Optional[models.VoterTurnout]:
    db_turnout = db.query(models.VoterTurnout).filter(models.VoterTurnout.id == turnout_id).first()
    if db_turnout:
        for key, value in turnout.dict().items():
            setattr(db_turnout, key, value)
        db.commit()
        db.refresh(db_turnout)
    return db_turnout

def delete_turnout(db: Session, turnout_id: int) -> bool:
    db_turnout = db.query(models.VoterTurnout).filter(models.VoterTurnout.id == turnout_id).first()
    if db_turnout:
        db.delete(db_turnout)
        db.commit()
        return True
    return False

# Users CRUD
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Dashboard Analytics Functions
def get_party_wise_seats(db: Session, election_id: int) -> List[schemas.PartySeatsData]:
    """Get party-wise seat count and vote share for an election."""
    result = db.query(
        models.Party.name.label("party_name"),
        models.Party.short_name.label("party_short_name"),
        func.count(models.Result.id).label("seats_won"),
        func.sum(models.Result.votes_received).label("total_votes"),
        func.avg(models.Result.vote_percentage).label("vote_percentage")
    ).join(
        models.Candidate, models.Party.id == models.Candidate.party_id
    ).join(
        models.Result, models.Candidate.id == models.Result.candidate_id
    ).filter(
        models.Result.election_id == election_id,
        models.Result.is_winner == True
    ).group_by(
        models.Party.id, models.Party.name, models.Party.short_name
    ).order_by(desc("seats_won")).all()
    
    return [schemas.PartySeatsData(
        party_name=r.party_name,
        party_short_name=r.party_short_name or r.party_name[:3].upper(),
        seats_won=r.seats_won,
        total_votes=r.total_votes or 0,
        vote_percentage=round(r.vote_percentage or 0, 2)
    ) for r in result]

def get_state_wise_results(db: Session, election_id: int) -> List[schemas.StateWiseResults]:
    """Get state-wise election results summary: one row per state, with
    'leading_party' being whichever party won the most seats in that state
    (not just any party that won at least one, which was the earlier bug)."""
    # Seats won per (state, party).
    seats_by_state_party = db.query(
        models.State.id.label("state_id"),
        models.State.name.label("state_name"),
        models.Party.name.label("party_name"),
        func.count(models.Result.id).label("seats")
    ).join(
        models.Constituency, models.State.id == models.Constituency.state_id
    ).join(
        models.Result, models.Constituency.id == models.Result.constituency_id
    ).join(
        models.Candidate, models.Result.candidate_id == models.Candidate.id
    ).join(
        models.Party, models.Candidate.party_id == models.Party.id
    ).filter(
        models.Result.election_id == election_id,
        models.Result.is_winner == True
    ).group_by(
        models.State.id, models.State.name, models.Party.name
    ).all()

    # Pick the top party per state in Python (simplest portable way to do a
    # per-group "top 1" without a database-specific window function).
    best_by_state = {}
    for row in seats_by_state_party:
        current = best_by_state.get(row.state_id)
        if current is None or row.seats > current["seats"]:
            best_by_state[row.state_id] = {
                "state_name": row.state_name,
                "leading_party": row.party_name,
                "seats": row.seats,
            }
    total_seats_by_state = {}
    for row in seats_by_state_party:
        total_seats_by_state[row.state_id] = total_seats_by_state.get(row.state_id, 0) + row.seats

    # Real turnout per state = total votes polled / total electors across
    # its constituencies (not an average of percentages, which skews toward
    # small constituencies).
    turnout_rows = db.query(
        models.State.id.label("state_id"),
        func.sum(models.VoterTurnout.total_votes_polled).label("votes_polled"),
        func.sum(models.VoterTurnout.total_electors).label("electors")
    ).join(
        models.Constituency, models.State.id == models.Constituency.state_id
    ).join(
        models.VoterTurnout, models.VoterTurnout.constituency_id == models.Constituency.id
    ).filter(
        models.VoterTurnout.election_id == election_id
    ).group_by(models.State.id).all()
    turnout_by_state = {
        r.state_id: (r.votes_polled / r.electors * 100) if r.electors else 0
        for r in turnout_rows
    }

    return [schemas.StateWiseResults(
        state_name=info["state_name"],
        total_seats=total_seats_by_state.get(state_id, info["seats"]),
        leading_party=info["leading_party"],
        turnout_percentage=round(turnout_by_state.get(state_id, 0), 2)
    ) for state_id, info in sorted(best_by_state.items(), key=lambda kv: kv[1]["state_name"])]

def _closest_or_landslide_contests(db: Session, election_id: int, limit: int, ascending: bool) -> List[schemas.ClosestContests]:
    """Shared query for both 'closest contests' (ascending margin) and
    'landslide/safest seats' (descending margin)."""
    query = db.query(
        models.Constituency.name.label("constituency_name"),
        models.State.name.label("state_name"),
        models.Candidate.name.label("winner_name"),
        models.Party.short_name.label("winner_party"),
        models.Result.margin,
        models.Result.vote_percentage,
        models.Result.votes_received
    ).join(
        models.Candidate, models.Result.candidate_id == models.Candidate.id
    ).join(
        models.Party, models.Candidate.party_id == models.Party.id
    ).join(
        models.Constituency, models.Result.constituency_id == models.Constituency.id
    ).join(
        models.State, models.Constituency.state_id == models.State.id
    ).filter(
        models.Result.election_id == election_id,
        models.Result.is_winner == True,
        models.Result.margin.is_not(None)
    )
    query = query.order_by(models.Result.margin.asc() if ascending else models.Result.margin.desc())
    result = query.limit(limit).all()

    return [schemas.ClosestContests(
        constituency_name=r.constituency_name,
        state_name=r.state_name,
        winner_name=r.winner_name,
        winner_party=r.winner_party or "IND",
        margin=r.margin,
        # margin as a share of all votes polled in the seat:
        #   total_votes_polled = votes_received * 100 / vote_percentage
        margin_percentage=round(
            (r.margin * r.vote_percentage / r.votes_received) if r.votes_received else 0, 2
        )
    ) for r in result]


def get_closest_contests(db: Session, election_id: int, limit: int = 10) -> List[schemas.ClosestContests]:
    """Get closest contests by victory margin (nail-biters)."""
    return _closest_or_landslide_contests(db, election_id, limit, ascending=True)


def get_landslide_contests(db: Session, election_id: int, limit: int = 10) -> List[schemas.ClosestContests]:
    """Get the most one-sided contests by victory margin (safest seats)."""
    return _closest_or_landslide_contests(db, election_id, limit, ascending=False)

def get_turnout_analysis(db: Session, election_id: int) -> List[schemas.TurnoutAnalysis]:
    """Get gender-wise turnout analysis."""
    result = db.query(
        models.State.name.label("state_name"),
        models.Constituency.name.label("constituency_name"),
        models.VoterTurnout.turnout_percentage,
        models.VoterTurnout.male_turnout_percentage,
        models.VoterTurnout.female_turnout_percentage
    ).join(
        models.Constituency, models.VoterTurnout.constituency_id == models.Constituency.id
    ).join(
        models.State, models.Constituency.state_id == models.State.id
    ).filter(
        models.VoterTurnout.election_id == election_id
    ).all()
    
    return [schemas.TurnoutAnalysis(
        state_name=r.state_name,
        constituency_name=r.constituency_name,
        total_turnout=round(r.turnout_percentage or 0, 2),
        male_turnout=round(r.male_turnout_percentage or 0, 2),
        female_turnout=round(r.female_turnout_percentage or 0, 2),
        gender_gap=round((r.male_turnout_percentage or 0) - (r.female_turnout_percentage or 0), 2)
    ) for r in result]

# --- National overview / KPI panel ------------------------------------------
NOTA_SHORT_NAME = "NOTA"


def get_election_overview(db: Session, election_id: int) -> schemas.ElectionOverview:
    """A single bundle of headline numbers for the top-of-dashboard KPI row.

    Pulls one row per (candidate, result, party) for the election and does
    all the counting in Python - simpler and safer than juggling a dozen
    separately-joined queries against the same tables."""
    rows = db.query(
        models.Candidate.gender,
        models.Candidate.age,
        models.Candidate.criminal_cases,
        models.Candidate.assets,
        models.Party.short_name.label("party_short_name"),
        models.Result.is_winner,
        models.Result.votes_received,
    ).join(
        models.Result, models.Result.candidate_id == models.Candidate.id
    ).join(
        models.Party, models.Candidate.party_id == models.Party.id
    ).filter(
        models.Result.election_id == election_id
    ).all()

    real = [r for r in rows if r.party_short_name != NOTA_SHORT_NAME]
    nota = [r for r in rows if r.party_short_name == NOTA_SHORT_NAME]
    winners = [r for r in real if r.is_winner]

    total_candidates = len(real)
    total_seats = sum(1 for r in rows if r.is_winner)
    total_votes_cast = sum(r.votes_received for r in rows)
    nota_votes = sum(r.votes_received for r in nota)

    # One declared winner = one reporting constituency.
    total_constituencies_reporting = total_seats

    electors_total = db.query(func.sum(models.VoterTurnout.total_electors)).filter(
        models.VoterTurnout.election_id == election_id
    ).scalar() or 0

    women_candidates = sum(1 for r in real if r.gender == "Female")
    women_winners = sum(1 for r in winners if r.gender == "Female")
    with_cases = sum(1 for r in real if (r.criminal_cases or 0) > 0)
    winners_with_cases = sum(1 for r in winners if (r.criminal_cases or 0) > 0)
    ages = [r.age for r in real if r.age is not None]
    avg_age = sum(ages) / len(ages) if ages else 0

    winner_assets = [r.assets for r in winners if r.assets is not None]
    median_assets = statistics.median(winner_assets) if winner_assets else 0
    crorepati_share = (
        (sum(1 for a in winner_assets if a >= 100) / len(winner_assets) * 100)
        if winner_assets else 0
    )

    independents_won = sum(1 for r in winners if r.party_short_name == "IND")

    return schemas.ElectionOverview(
        total_seats=total_seats,
        total_constituencies_reporting=total_constituencies_reporting,
        total_candidates=total_candidates,
        total_votes_cast=int(total_votes_cast),
        overall_turnout_percentage=round(total_votes_cast / electors_total * 100, 2) if electors_total else 0,
        nota_votes=int(nota_votes),
        nota_percentage=round(nota_votes / total_votes_cast * 100, 2) if total_votes_cast else 0,
        women_candidates=women_candidates,
        women_winners=women_winners,
        women_candidate_share=round(women_candidates / total_candidates * 100, 2) if total_candidates else 0,
        women_winner_share=round(women_winners / total_seats * 100, 2) if total_seats else 0,
        candidates_with_criminal_cases=with_cases,
        criminal_case_share=round(with_cases / total_candidates * 100, 2) if total_candidates else 0,
        winners_with_criminal_cases=winners_with_cases,
        winner_criminal_case_share=round(winners_with_cases / total_seats * 100, 2) if total_seats else 0,
        avg_candidate_age=round(avg_age, 1),
        median_winner_assets_lakhs=round(median_assets, 2),
        winners_crorepati_share=round(crorepati_share, 2),
        independents_won=independents_won,
    )


# --- Gender representation by party -----------------------------------------
def get_gender_representation(db: Session, election_id: int, top_n: int = 12) -> List[schemas.GenderRepresentationByParty]:
    """Women fielded vs. women elected, for the parties with the most seats."""
    rows = db.query(
        models.Party.short_name.label("party_short_name"),
        models.Candidate.gender,
        models.Result.is_winner
    ).join(
        models.Candidate, models.Result.candidate_id == models.Candidate.id
    ).join(
        models.Party, models.Candidate.party_id == models.Party.id
    ).filter(
        models.Result.election_id == election_id,
        models.Party.short_name != NOTA_SHORT_NAME
    ).all()

    by_party = {}
    for r in rows:
        p = by_party.setdefault(r.party_short_name, {
            "total_contested": 0, "total_won": 0, "women_contested": 0, "women_won": 0
        })
        p["total_contested"] += 1
        is_woman = r.gender == "Female"
        if is_woman:
            p["women_contested"] += 1
        if r.is_winner:
            p["total_won"] += 1
            if is_woman:
                p["women_won"] += 1

    ranked = sorted(by_party.items(), key=lambda kv: kv[1]["total_won"], reverse=True)[:top_n]
    return [schemas.GenderRepresentationByParty(
        party_short_name=name,
        total_contested=v["total_contested"],
        total_won=v["total_won"],
        women_contested=v["women_contested"],
        women_won=v["women_won"],
        women_candidate_share=round(v["women_contested"] / v["total_contested"] * 100, 2) if v["total_contested"] else 0,
    ) for name, v in ranked]


# --- Education profile of winners -------------------------------------------
def get_education_breakdown(db: Session, election_id: int) -> List[schemas.EducationBreakdown]:
    rows = db.query(
        models.Candidate.education,
        func.count(models.Result.id).label("winners")
    ).join(
        models.Result, models.Result.candidate_id == models.Candidate.id
    ).filter(
        models.Result.election_id == election_id,
        models.Result.is_winner == True,
        models.Candidate.education.is_not(None)
    ).group_by(models.Candidate.education).all()

    total = sum(r.winners for r in rows) or 1
    ranked = sorted(rows, key=lambda r: r.winners, reverse=True)
    return [schemas.EducationBreakdown(
        education=r.education, winners=r.winners, share=round(r.winners / total * 100, 2)
    ) for r in ranked]


# --- Candidate wealth --------------------------------------------------
def get_wealth_leaders(db: Session, election_id: int, limit: int = 10, winners_only: bool = True) -> List[schemas.WealthLeader]:
    query = db.query(
        models.Candidate.name.label("candidate_name"),
        models.Party.short_name.label("party_short_name"),
        models.State.name.label("state_name"),
        models.Constituency.name.label("constituency_name"),
        models.Candidate.assets,
        models.Result.is_winner
    ).join(
        models.Result, models.Result.candidate_id == models.Candidate.id
    ).join(
        models.Party, models.Candidate.party_id == models.Party.id
    ).join(
        models.Constituency, models.Candidate.constituency_id == models.Constituency.id
    ).join(
        models.State, models.Constituency.state_id == models.State.id
    ).filter(
        models.Result.election_id == election_id,
        models.Candidate.assets.is_not(None)
    )
    if winners_only:
        query = query.filter(models.Result.is_winner == True)
    rows = query.order_by(models.Candidate.assets.desc()).limit(limit).all()

    return [schemas.WealthLeader(
        candidate_name=r.candidate_name,
        party_short_name=r.party_short_name or "IND",
        state_name=r.state_name,
        constituency_name=r.constituency_name,
        assets_lakhs=round(r.assets, 2),
        is_winner=r.is_winner,
    ) for r in rows]


# --- Criminal cases by party --------------------------------------------
def get_criminal_cases_by_party(db: Session, election_id: int, top_n: int = 12) -> List[schemas.CriminalCasesByParty]:
    rows = db.query(
        models.Party.short_name.label("party_short_name"),
        models.Candidate.criminal_cases
    ).join(
        models.Result, models.Result.candidate_id == models.Candidate.id
    ).join(
        models.Party, models.Candidate.party_id == models.Party.id
    ).filter(
        models.Result.election_id == election_id,
        models.Party.short_name != NOTA_SHORT_NAME
    ).all()

    by_party = {}
    for r in rows:
        p = by_party.setdefault(r.party_short_name, {"total": 0, "with_cases": 0})
        p["total"] += 1
        if (r.criminal_cases or 0) > 0:
            p["with_cases"] += 1

    ranked = sorted(by_party.items(), key=lambda kv: kv[1]["total"], reverse=True)[:top_n]
    return [schemas.CriminalCasesByParty(
        party_short_name=name,
        total_candidates=v["total"],
        candidates_with_cases=v["with_cases"],
        share_with_cases=round(v["with_cases"] / v["total"] * 100, 2) if v["total"] else 0,
    ) for name, v in ranked]


# --- Constituency search / lookup ---------------------------------------
def search_constituencies(db: Session, election_id: int, query: str, limit: int = 15) -> List[schemas.ConstituencySearchResult]:
    like = f"%{query.strip()}%"
    rows = db.query(
        models.Constituency.name.label("constituency_name"),
        models.State.name.label("state_name"),
        models.Candidate.name.label("winner_name"),
        models.Party.short_name.label("winner_party"),
    ).join(
        models.State, models.Constituency.state_id == models.State.id
    ).outerjoin(
        models.Result,
        (models.Result.constituency_id == models.Constituency.id) &
        (models.Result.election_id == election_id) &
        (models.Result.is_winner == True)
    ).outerjoin(
        models.Candidate, models.Result.candidate_id == models.Candidate.id
    ).outerjoin(
        models.Party, models.Candidate.party_id == models.Party.id
    ).filter(
        models.Constituency.name.ilike(like)
    ).order_by(models.Constituency.name).limit(limit).all()

    return [schemas.ConstituencySearchResult(
        constituency_name=r.constituency_name,
        state_name=r.state_name,
        winner_name=r.winner_name,
        winner_party=r.winner_party,
    ) for r in rows]


def get_constituency_lookup(db: Session, election_id: int, constituency_name: str) -> Optional[schemas.ConstituencyLookup]:
    constituency = db.query(models.Constituency).filter(
        func.lower(models.Constituency.name) == constituency_name.strip().lower()
    ).first()
    if not constituency:
        return None

    turnout = db.query(models.VoterTurnout).filter(
        models.VoterTurnout.constituency_id == constituency.id,
        models.VoterTurnout.election_id == election_id
    ).first()

    rows = db.query(
        models.Candidate.name.label("candidate_name"),
        models.Party.short_name.label("party_short_name"),
        models.Party.name.label("party_name"),
        models.Result.votes_received,
        models.Result.vote_percentage,
        models.Result.is_winner,
        models.Candidate.gender,
        models.Candidate.age,
        models.Candidate.education,
        models.Candidate.criminal_cases,
        models.Candidate.assets,
    ).join(
        models.Result, models.Result.candidate_id == models.Candidate.id
    ).join(
        models.Party, models.Candidate.party_id == models.Party.id
    ).filter(
        models.Result.constituency_id == constituency.id,
        models.Result.election_id == election_id
    ).order_by(models.Result.votes_received.desc()).all()

    return schemas.ConstituencyLookup(
        constituency_name=constituency.name,
        state_name=constituency.state.name if constituency.state else "",
        reserved_for=constituency.reserved_for,
        total_electors=turnout.total_electors if turnout else None,
        total_votes_polled=turnout.total_votes_polled if turnout else None,
        turnout_percentage=turnout.turnout_percentage if turnout else None,
        results=[schemas.ConstituencyCandidateResult(
            candidate_name=r.candidate_name,
            party_short_name=r.party_short_name or "IND",
            party_name=r.party_name,
            votes_received=r.votes_received,
            vote_percentage=round(r.vote_percentage or 0, 2),
            is_winner=r.is_winner,
            gender=r.gender,
            age=r.age,
            education=r.education,
            criminal_cases=r.criminal_cases,
            assets_lakhs=r.assets,
        ) for r in rows]
    )
