"""
Loads real 2019 Lok Sabha (Indian general election) results into the database.

Data sources (both freely redistributable, no API key needed):

  data/LS_2.0.csv
      Candidate-level results for all 543 constituencies, sourced from
      candidate affidavits filed with the Election Commission of India and
      compiled by the Association for Democratic Reforms (ADR / myneta.info).
      Columns: state, constituency, candidate name, winner flag, party,
      symbol, gender, criminal cases, age, reserved category, education,
      assets, liabilities, votes, and total electors.

  data/state_turnout_2019.csv
      State-wise actual voter turnout with a male/female/other split of
      votes cast, published by the Election Commission of India.

Run with:  python populate_data.py
(Docker:   docker compose exec web python populate_data.py)

What's real vs. estimated
--------------------------
Every vote count, margin, candidate attribute (age/gender/education/
criminal cases/assets), and constituency elector count is taken directly
from the source files above - nothing is invented.

The one place this script estimates rather than reports: per-constituency
turnout is split by gender using that CONSTITUENCY's state-wide actual
male/female vote share (real, from state_turnout_2019.csv), and the
elector-side split assumes the commonly-cited national average of 52%
male / 48% female electors, since the Election Commission does not publish
electors-by-gender at constituency level. This is flagged in the UI
wherever it's shown.
"""
import os
import re
from datetime import datetime

import pandas as pd

from app.database import SessionLocal, create_tables, drop_tables
from app import models, auth

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CANDIDATES_CSV = os.path.join(DATA_DIR, "LS_2.0.csv")
TURNOUT_CSV = os.path.join(DATA_DIR, "state_turnout_2019.csv")

# --------------------------------------------------------------------------
# Reference data: state metadata and party full names.
# Anything not listed falls back to a sensible default (the code itself
# stands in for the full name) rather than failing the import.
# --------------------------------------------------------------------------

STATE_META = {
    # name as it appears in LS_2.0.csv -> (code, region)
    "Andhra Pradesh": ("AP", "South"), "Arunachal Pradesh": ("AR", "Northeast"),
    "Assam": ("AS", "Northeast"), "Bihar": ("BR", "East"),
    "Chhattisgarh": ("CG", "Central"), "Goa": ("GA", "West"),
    "Gujarat": ("GJ", "West"), "Haryana": ("HR", "North"),
    "Himachal Pradesh": ("HP", "North"), "Jharkhand": ("JH", "East"),
    "Karnataka": ("KA", "South"), "Kerala": ("KL", "South"),
    "Madhya Pradesh": ("MP", "Central"), "Maharashtra": ("MH", "West"),
    "Manipur": ("MN", "Northeast"), "Meghalaya": ("ML", "Northeast"),
    "Mizoram": ("MZ", "Northeast"), "Nagaland": ("NL", "Northeast"),
    "Odisha": ("OD", "East"), "Punjab": ("PB", "North"),
    "Rajasthan": ("RJ", "North"), "Sikkim": ("SK", "Northeast"),
    "Tamil Nadu": ("TN", "South"), "Telangana": ("TS", "South"),
    "Tripura": ("TR", "Northeast"), "Uttar Pradesh": ("UP", "North"),
    "Uttarakhand": ("UK", "North"), "West Bengal": ("WB", "East"),
    "NCT OF Delhi": ("DL", "North"), "Jammu & Kashmir": ("JK", "North"),
    "Chandigarh": ("CH", "North"), "Andaman & Nicobar Islands": ("AN", "South"),
    "Dadra & Nagar Haveli": ("DN", "West"), "Daman & Diu": ("DD", "West"),
    "Lakshadweep": ("LD", "South"), "Puducherry": ("PY", "South"),
}

# ECI-recognised national parties as of the 2019 general election.
NATIONAL_PARTIES = {"BJP", "INC", "BSP", "CPI", "CPI(M)", "NCP", "AITC"}

PARTY_FULL_NAMES = {
    "BJP": "Bharatiya Janata Party", "INC": "Indian National Congress",
    "BSP": "Bahujan Samaj Party", "CPI(M)": "Communist Party of India (Marxist)",
    "CPI": "Communist Party of India", "VBA": "Vanchit Bahujan Aaghadi",
    "AITC": "All India Trinamool Congress", "SP": "Samajwadi Party",
    "NTK": "Naam Tamilar Katchi", "MNM": "Makkal Needhi Maiam",
    "SHS": "Shiv Sena", "YSRCP": "Yuvajana Sramika Rythu Congress Party",
    "TDP": "Telugu Desam Party", "AAP": "Aam Aadmi Party",
    "DMK": "Dravida Munnetra Kazhagam", "NCP": "Nationalist Congress Party",
    "AIADMK": "All India Anna Dravida Munnetra Kazhagam",
    "RJD": "Rashtriya Janata Dal", "BJD": "Biju Janata Dal",
    "JnP": "Jannayak Janta Party", "JD(U)": "Janata Dal (United)",
    "TRS": "Telangana Rashtra Samithi", "SBSP": "Suheldev Bharatiya Samaj Party",
    "SAD": "Shiromani Akali Dal", "APoI": "All People's Party",
    "JD(S)": "Janata Dal (Secular)", "PMK": "Pattali Makkal Katchi",
    "LJP": "Lok Janshakti Party", "JMM": "Jharkhand Mukti Morcha",
    "INLD": "Indian National Lok Dal", "AIMIM": "All India Majlis-e-Ittehadul Muslimeen",
    "RLD": "Rashtriya Lok Dal", "AGP": "Asom Gana Parishad",
    "AIUDF": "All India United Democratic Front", "IUML": "Indian Union Muslim League",
    "JKN": "Jammu & Kashmir National Conference", "JKPDP": "Jammu & Kashmir Peoples Democratic Party",
    "MNF": "Mizo National Front", "NPF": "Naga People's Front",
    "NDPP": "Nationalist Democratic Progressive Party", "SDF": "Sikkim Democratic Front",
    "SKM": "Sikkim Krantikari Morcha", "PDP": "Jammu & Kashmir Peoples Democratic Party",
    "IND": "Independent", "NOTA": "None of the Above",
}


def parse_rupees_to_lakhs(raw):
    """'Rs 30,99,414\\n ~ 30 Lacs+' -> 30.99 (lakhs). None if unparseable."""
    if pd.isna(raw):
        return None
    s = str(raw).strip()
    if s.lower() in ("nil", ""):
        return 0.0
    m = re.match(r"Rs\s*([\d,]+)", s)
    if not m:
        return None
    rupees = int(m.group(1).replace(",", ""))
    return round(rupees / 100_000, 2)


def parse_criminal_cases(raw):
    if pd.isna(raw):
        return None
    s = str(raw).strip()
    if not s.isdigit():
        return None
    return int(s)


def normalize_state_name(name):
    """Aligns state_turnout_2019.csv's names with LS_2.0.csv's."""
    s = name.strip().rstrip("*").strip()
    if s == "Delhi":
        return "NCT OF Delhi"
    return s


def load_turnout_by_state():
    """State -> real (male_vote_share, female_vote_share) from actual votes cast."""
    df = pd.read_csv(TURNOUT_CSV)
    df.columns = [c.strip() for c in df.columns]
    shares = {}
    for _, row in df.iterrows():
        state = normalize_state_name(row["State Name"])
        male, female = row["Male"], row["Female"]
        total = male + female
        if total > 0:
            shares[state] = (male / total, female / total)
    return shares


def main():
    print("Resetting schema...")
    drop_tables()
    create_tables()

    print(f"Reading {CANDIDATES_CSV} ...")
    df = pd.read_csv(CANDIDATES_CSV)
    df.columns = [c.replace("\n", " ").strip() for c in df.columns]
    # Collapse the wrapped multi-line headers down to clean names.
    df = df.rename(columns={
        "CRIMINAL CASES": "CRIMINAL_CASES",
        "GENERAL VOTES": "GENERAL_VOTES",
        "POSTAL VOTES": "POSTAL_VOTES",
        "TOTAL VOTES": "TOTAL_VOTES",
        "OVER TOTAL ELECTORS  IN CONSTITUENCY": "PCT_OF_ELECTORS",
        "OVER TOTAL VOTES POLLED  IN CONSTITUENCY": "PCT_OF_VOTES_POLLED",
        "TOTAL ELECTORS": "TOTAL_ELECTORS",
    })

    turnout_shares = load_turnout_by_state()
    default_share = (0.52, 0.48)  # national fallback if a state is missing

    db = SessionLocal()
    try:
        # --- States ---------------------------------------------------
        state_rows = {}
        for name in sorted(df["STATE"].unique()):
            code, region = STATE_META.get(name, (name[:2].upper(), None))
            s = models.State(name=name, code=code, region=region)
            db.add(s)
            state_rows[name] = s
        db.flush()
        print(f"Created {len(state_rows)} states")

        # --- Parties ----------------------------------------------------
        party_rows = {}
        for code in sorted(df["PARTY"].unique()):
            p = models.Party(
                name=PARTY_FULL_NAMES.get(code, code),
                short_name=code,
                national_party=code in NATIONAL_PARTIES,
            )
            db.add(p)
            party_rows[code] = p
        db.flush()
        print(f"Created {len(party_rows)} parties")

        # --- Election -----------------------------------------------------
        election = models.Election(
            name="2019 Indian General Election (17th Lok Sabha)",
            year=2019,
            election_type="Lok Sabha",
            start_date=datetime(2019, 4, 11),
            end_date=datetime(2019, 5, 19),  # counting/results: May 23, 2019
            total_constituencies=df["CONSTITUENCY"].nunique(),
        )
        db.add(election)
        db.flush()
        print(f"Created election: {election.name}")

        # --- Constituencies, Candidates, Results, Turnout ------------------
        n_constituencies = n_candidates = n_results = n_turnout = 0

        for (state_name, const_name), group in df.groupby(["STATE", "CONSTITUENCY"], sort=False):
            real = group[group["PARTY"] != "NOTA"]
            reserved_for = "General"
            if not real["CATEGORY"].dropna().empty:
                reserved_for = real["CATEGORY"].mode().iat[0].title()

            constituency = models.Constituency(
                name=const_name,
                constituency_type="Lok Sabha",
                state_id=state_rows[state_name].id,
                reserved_for=reserved_for,
            )
            db.add(constituency)
            db.flush()
            n_constituencies += 1

            # Rank every row (including NOTA) by actual votes polled.
            ranked = group.sort_values("TOTAL_VOTES", ascending=False).reset_index(drop=True)
            total_votes_polled = int(ranked["TOTAL_VOTES"].sum())
            total_electors = int(ranked["TOTAL_ELECTORS"].iloc[0])
            runner_up_votes = int(ranked["TOTAL_VOTES"].iloc[1]) if len(ranked) > 1 else 0

            for position, row in ranked.iterrows():
                is_nota = row["PARTY"] == "NOTA"
                candidate = models.Candidate(
                    name=row["NAME"],
                    age=None if pd.isna(row.get("AGE")) else int(row["AGE"]),
                    gender=None if is_nota or pd.isna(row.get("GENDER")) else str(row["GENDER"]).title(),
                    education=None if is_nota or pd.isna(row.get("EDUCATION")) else str(row["EDUCATION"]).strip(),
                    occupation=None,  # not present in source data
                    criminal_cases=parse_criminal_cases(row.get("CRIMINAL_CASES")),
                    assets=parse_rupees_to_lakhs(row.get("ASSETS")),
                    party_id=party_rows[row["PARTY"]].id,
                    constituency_id=constituency.id,
                )
                db.add(candidate)
                db.flush()
                n_candidates += 1

                # The source's own WINNER flag has at least one known error
                # (Bihar/Aurangabad has two rows flagged as winner). Since
                # this is first-past-the-post, "most votes in the
                # constituency" is the unambiguous, self-consistent
                # definition - use that instead of trusting the flag.
                is_winner = bool(position == 0)
                result = models.Result(
                    votes_received=int(row["TOTAL_VOTES"]),
                    vote_percentage=float(row["PCT_OF_VOTES_POLLED"]),
                    position=position + 1,
                    margin=(int(row["TOTAL_VOTES"]) - runner_up_votes) if is_winner else None,
                    is_winner=is_winner,
                    election_id=election.id,
                    constituency_id=constituency.id,
                    candidate_id=candidate.id,
                )
                db.add(result)
                n_results += 1

            # --- Voter turnout: real totals; gender split estimated (see module docstring) ---
            male_share, female_share = turnout_shares.get(state_name, default_share)
            male_votes = round(total_votes_polled * male_share)
            female_votes = total_votes_polled - male_votes
            male_electors = round(total_electors * 0.52)
            female_electors = total_electors - male_electors

            turnout = models.VoterTurnout(
                total_electors=total_electors,
                total_votes_polled=total_votes_polled,
                turnout_percentage=round(total_votes_polled / total_electors * 100, 2) if total_electors else None,
                male_electors=male_electors,
                female_electors=female_electors,
                male_votes=male_votes,
                female_votes=female_votes,
                male_turnout_percentage=round(male_votes / male_electors * 100, 2) if male_electors else None,
                female_turnout_percentage=round(female_votes / female_electors * 100, 2) if female_electors else None,
                election_id=election.id,
                constituency_id=constituency.id,
            )
            db.add(turnout)
            n_turnout += 1

            if n_constituencies % 100 == 0:
                db.commit()
                print(f"  ... {n_constituencies} constituencies loaded")

        db.commit()
        print(f"Created {n_constituencies} constituencies")
        print(f"Created {n_candidates} candidates")
        print(f"Created {n_results} results")
        print(f"Created {n_turnout} voter turnout records")

        # drop_tables() above also wipes the users table, and the app only
        # creates the default admin account once, on startup - so without
        # this, login breaks the moment this script runs after the server
        # is already up.
        auth.create_default_user(db)

        print("\nReal 2019 Lok Sabha election data loaded successfully!")
        print("Login credentials: username=admin, password=admin123")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
