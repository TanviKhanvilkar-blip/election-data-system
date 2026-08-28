-- Sample SQL Queries for Election Data Management System
-- These queries demonstrate database operations used in the project

-- ============================================================================
-- 1. DATABASE SCHEMA CREATION QUERIES
-- ============================================================================

-- Create States table
CREATE TABLE states (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    region VARCHAR(50),
    capital VARCHAR(100),
    total_constituencies INTEGER
);

-- Create Parties table
CREATE TABLE parties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    short_name VARCHAR(20),
    symbol VARCHAR(100),
    founded_year INTEGER,
    ideology VARCHAR(100),
    national_party BOOLEAN DEFAULT FALSE
);

-- Create Elections table
CREATE TABLE elections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    year INTEGER NOT NULL,
    election_type VARCHAR(50) NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    total_constituencies INTEGER,
    total_candidates INTEGER
);

-- Create Constituencies table
CREATE TABLE constituencies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20),
    constituency_type VARCHAR(20) NOT NULL,
    state_id INTEGER REFERENCES states(id),
    reserved_for VARCHAR(20) DEFAULT 'General'
);

-- Create Candidates table
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    education VARCHAR(200),
    occupation VARCHAR(200),
    criminal_cases INTEGER DEFAULT 0,
    assets FLOAT,
    party_id INTEGER REFERENCES parties(id),
    constituency_id INTEGER REFERENCES constituencies(id)
);

-- Create Results table
CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    votes_received INTEGER NOT NULL,
    vote_percentage FLOAT,
    position INTEGER,
    margin INTEGER,
    is_winner BOOLEAN DEFAULT FALSE,
    election_id INTEGER REFERENCES elections(id),
    constituency_id INTEGER REFERENCES constituencies(id),
    candidate_id INTEGER REFERENCES candidates(id)
);

-- Create Voter Turnout table
CREATE TABLE voter_turnout (
    id SERIAL PRIMARY KEY,
    total_electors INTEGER,
    total_votes_polled INTEGER,
    turnout_percentage FLOAT,
    male_electors INTEGER,
    female_electors INTEGER,
    male_votes INTEGER,
    female_votes INTEGER,
    male_turnout_percentage FLOAT,
    female_turnout_percentage FLOAT,
    election_id INTEGER REFERENCES elections(id),
    constituency_id INTEGER REFERENCES constituencies(id)
);

-- Create Users table for authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 2. INDEXING QUERIES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Create indexes for frequently queried columns
CREATE INDEX idx_candidates_party_id ON candidates(party_id);
CREATE INDEX idx_candidates_constituency_id ON candidates(constituency_id);
CREATE INDEX idx_results_election_id ON results(election_id);
CREATE INDEX idx_results_constituency_id ON results(constituency_id);
CREATE INDEX idx_results_candidate_id ON results(candidate_id);
CREATE INDEX idx_results_is_winner ON results(is_winner);
CREATE INDEX idx_voter_turnout_election_id ON voter_turnout(election_id);
CREATE INDEX idx_constituencies_state_id ON constituencies(state_id);

-- Composite indexes for complex queries
CREATE INDEX idx_results_election_winner ON results(election_id, is_winner);
CREATE INDEX idx_candidates_party_constituency ON candidates(party_id, constituency_id);

-- ============================================================================
-- 3. BASIC CRUD OPERATIONS
-- ============================================================================

-- INSERT Operations
-- Add a new state
INSERT INTO states (name, code, region, capital, total_constituencies)
VALUES ('Maharashtra', 'MH', 'West', 'Mumbai', 48);

-- Add a new political party
INSERT INTO parties (name, short_name, symbol, founded_year, ideology, national_party)
VALUES ('Bharatiya Janata Party', 'BJP', 'Lotus', 1980, 'Hindu Nationalism', TRUE);

-- Add a new election
INSERT INTO elections (name, year, election_type, start_date, end_date, total_constituencies, total_candidates)
VALUES ('Lok Sabha General Election 2024', 2024, 'Lok Sabha', '2024-04-19', '2024-06-01', 543, 8337);

-- SELECT Operations
-- Get all states in a specific region
SELECT * FROM states WHERE region = 'South';

-- Get all national parties
SELECT name, short_name, founded_year FROM parties WHERE national_party = TRUE;

-- Get all Lok Sabha elections
SELECT * FROM elections WHERE election_type = 'Lok Sabha' ORDER BY year DESC;

-- UPDATE Operations
-- Update a state's total constituencies
UPDATE states SET total_constituencies = 50 WHERE code = 'UP';

-- Update a party's ideology
UPDATE parties SET ideology = 'Social Democracy' WHERE short_name = 'INC';

-- DELETE Operations
-- Delete a candidate (with proper foreign key handling)
DELETE FROM results WHERE candidate_id = 1;
DELETE FROM candidates WHERE id = 1;

-- ============================================================================
-- 4. COMPLEX ANALYTICAL QUERIES (Used in Dashboard)
-- ============================================================================

-- Query 1: Party-wise seat count and vote share for 2024 election
SELECT 
    p.name as party_name,
    p.short_name as party_short_name,
    COUNT(r.id) as seats_won,
    SUM(r.votes_received) as total_votes,
    AVG(r.vote_percentage) as avg_vote_percentage
FROM parties p
JOIN candidates c ON p.id = c.party_id
JOIN results r ON c.id = r.candidate_id
JOIN elections e ON r.election_id = e.id
WHERE e.year = 2024 AND e.election_type = 'Lok Sabha' AND r.is_winner = TRUE
GROUP BY p.id, p.name, p.short_name
ORDER BY seats_won DESC;

-- Query 2: State-wise turnout analysis with gender breakdown
SELECT 
    s.name as state_name,
    AVG(vt.turnout_percentage) as avg_turnout,
    AVG(vt.male_turnout_percentage) as avg_male_turnout,
    AVG(vt.female_turnout_percentage) as avg_female_turnout,
    AVG(vt.male_turnout_percentage - vt.female_turnout_percentage) as gender_gap
FROM states s
JOIN constituencies c ON s.id = c.state_id
JOIN voter_turnout vt ON c.id = vt.constituency_id
JOIN elections e ON vt.election_id = e.id
WHERE e.year = 2024
GROUP BY s.id, s.name
ORDER BY avg_turnout DESC;

-- Query 3: Closest contests by victory margin
SELECT 
    cons.name as constituency_name,
    s.name as state_name,
    cand.name as winner_name,
    p.short_name as winner_party,
    r.margin as victory_margin,
    r.votes_received as winner_votes,
    (r.margin * 100.0 / r.votes_received) as margin_percentage
FROM results r
JOIN candidates cand ON r.candidate_id = cand.id
JOIN parties p ON cand.party_id = p.id
JOIN constituencies cons ON r.constituency_id = cons.id
JOIN states s ON cons.state_id = s.id
JOIN elections e ON r.election_id = e.id
WHERE r.is_winner = TRUE AND e.year = 2024 AND r.margin IS NOT NULL
ORDER BY r.margin ASC
LIMIT 10;

-- Query 4: Candidate demographics analysis
SELECT 
    gender,
    COUNT(*) as total_candidates,
    AVG(age) as avg_age,
    AVG(assets) as avg_assets,
    SUM(CASE WHEN criminal_cases > 0 THEN 1 ELSE 0 END) as with_criminal_cases,
    COUNT(r.id) as winners
FROM candidates c
LEFT JOIN results r ON c.id = r.candidate_id AND r.is_winner = TRUE
JOIN constituencies cons ON c.constituency_id = cons.id
JOIN results res ON c.id = res.candidate_id
JOIN elections e ON res.election_id = e.id
WHERE e.year = 2024
GROUP BY gender;

-- Query 5: Regional political dominance analysis
SELECT 
    s.region,
    p.short_name as dominant_party,
    COUNT(r.id) as seats_won,
    SUM(COUNT(r.id)) OVER (PARTITION BY s.region) as total_seats_in_region,
    (COUNT(r.id) * 100.0 / SUM(COUNT(r.id)) OVER (PARTITION BY s.region)) as dominance_percentage
FROM states s
JOIN constituencies c ON s.id = c.state_id
JOIN results r ON c.id = r.constituency_id
JOIN candidates cand ON r.candidate_id = cand.id
JOIN parties p ON cand.party_id = p.id
JOIN elections e ON r.election_id = e.id
WHERE e.year = 2024 AND r.is_winner = TRUE
GROUP BY s.region, p.id, p.short_name
ORDER BY s.region, seats_won DESC;

-- ============================================================================
-- 5. DATA VALIDATION AND QUALITY CHECKS
-- ============================================================================

-- Check for data consistency issues
-- Verify that all winners have position = 1
SELECT constituency_id, COUNT(*) as winner_count
FROM results 
WHERE is_winner = TRUE 
GROUP BY constituency_id, election_id
HAVING COUNT(*) != 1;

-- Check for missing foreign key references
SELECT c.id, c.name 
FROM candidates c 
LEFT JOIN parties p ON c.party_id = p.id 
WHERE p.id IS NULL;

-- Verify turnout calculations
SELECT 
    id,
    total_electors,
    total_votes_polled,
    turnout_percentage,
    (total_votes_polled * 100.0 / total_electors) as calculated_turnout
FROM voter_turnout
WHERE ABS(turnout_percentage - (total_votes_polled * 100.0 / total_electors)) > 1;

-- ============================================================================
-- 6. PERFORMANCE MONITORING QUERIES
-- ============================================================================

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;

-- Check record counts across all tables
SELECT 'states' as table_name, COUNT(*) as record_count FROM states
UNION ALL SELECT 'parties', COUNT(*) FROM parties
UNION ALL SELECT 'elections', COUNT(*) FROM elections
UNION ALL SELECT 'constituencies', COUNT(*) FROM constituencies
UNION ALL SELECT 'candidates', COUNT(*) FROM candidates
UNION ALL SELECT 'results', COUNT(*) FROM results
UNION ALL SELECT 'voter_turnout', COUNT(*) FROM voter_turnout
UNION ALL SELECT 'users', COUNT(*) FROM users;

-- ============================================================================
-- 7. ADVANCED ANALYTICAL QUERIES
-- ============================================================================

-- Query 7: Swing analysis between elections (if multiple elections data available)
WITH party_performance AS (
    SELECT 
        p.short_name,
        e.year,
        COUNT(CASE WHEN r.is_winner = TRUE THEN 1 END) as seats_won,
        SUM(r.votes_received) as total_votes
    FROM parties p
    JOIN candidates c ON p.id = c.party_id
    JOIN results r ON c.id = r.candidate_id
    JOIN elections e ON r.election_id = e.id
    WHERE e.election_type = 'Lok Sabha'
    GROUP BY p.id, p.short_name, e.year
)
SELECT 
    pp1.short_name as party,
    pp1.year as election_year_1,
    pp1.seats_won as seats_2019,
    pp2.year as election_year_2,
    pp2.seats_won as seats_2024,
    (pp2.seats_won - pp1.seats_won) as seat_change
FROM party_performance pp1
JOIN party_performance pp2 ON pp1.short_name = pp2.short_name
WHERE pp1.year = 2019 AND pp2.year = 2024
ORDER BY seat_change DESC;

-- Query 8: Constituency competitiveness index
SELECT 
    c.name as constituency_name,
    s.name as state_name,
    r1.votes_received as winner_votes,
    r2.votes_received as runner_up_votes,
    (r1.votes_received - r2.votes_received) as margin,
    vt.total_votes_polled,
    ((r1.votes_received - r2.votes_received) * 100.0 / vt.total_votes_polled) as margin_percentage,
    CASE 
        WHEN (r1.votes_received - r2.votes_received) * 100.0 / vt.total_votes_polled < 5 THEN 'Highly Competitive'
        WHEN (r1.votes_received - r2.votes_received) * 100.0 / vt.total_votes_polled < 10 THEN 'Competitive'
        WHEN (r1.votes_received - r2.votes_received) * 100.0 / vt.total_votes_polled < 20 THEN 'Moderately Safe'
        ELSE 'Safe Seat'
    END as competitiveness_category
FROM constituencies c
JOIN states s ON c.state_id = s.id
JOIN results r1 ON c.id = r1.constituency_id
JOIN results r2 ON c.id = r2.constituency_id
JOIN elections e ON r1.election_id = e.id
JOIN voter_turnout vt ON c.id = vt.constituency_id AND e.id = vt.election_id
WHERE e.year = 2024 
    AND r1.position = 1 
    AND r2.position = 2
    AND r1.election_id = r2.election_id
ORDER BY margin_percentage ASC;

-- Query 9: Education-wise candidate analysis
SELECT 
    education,
    COUNT(*) as total_candidates,
    COUNT(CASE WHEN r.is_winner = TRUE THEN 1 END) as winners,
    (COUNT(CASE WHEN r.is_winner = TRUE THEN 1 END) * 100.0 / COUNT(*)) as win_percentage,
    AVG(assets) as avg_assets
FROM candidates c
JOIN results r ON c.id = r.candidate_id
JOIN elections e ON r.election_id = e.id
WHERE e.year = 2024
GROUP BY education
ORDER BY win_percentage DESC;

-- Query 10: Voter turnout correlation with competitiveness
SELECT 
    CASE 
        WHEN margin_percentage < 5 THEN 'Highly Competitive (0-5%)'
        WHEN margin_percentage < 10 THEN 'Competitive (5-10%)'
        WHEN margin_percentage < 20 THEN 'Moderately Safe (10-20%)'
        ELSE 'Safe Seat (20%+)'
    END as competitiveness_bucket,
    COUNT(*) as constituency_count,
    AVG(vt.turnout_percentage) as avg_turnout,
    MIN(vt.turnout_percentage) as min_turnout,
    MAX(vt.turnout_percentage) as max_turnout
FROM (
    SELECT 
        c.id,
        vt.turnout_percentage,
        ((r1.votes_received - r2.votes_received) * 100.0 / vt.total_votes_polled) as margin_percentage
    FROM constituencies c
    JOIN results r1 ON c.id = r1.constituency_id
    JOIN results r2 ON c.id = r2.constituency_id
    JOIN elections e ON r1.election_id = e.id
    JOIN voter_turnout vt ON c.id = vt.constituency_id AND e.id = vt.election_id
    WHERE e.year = 2024 
        AND r1.position = 1 
        AND r2.position = 2
        AND r1.election_id = r2.election_id
) competitiveness_data
JOIN voter_turnout vt ON competitiveness_data.id = vt.constituency_id
GROUP BY competitiveness_bucket
ORDER BY avg_turnout DESC;

-- ============================================================================
-- 8. DATA EXPORT QUERIES FOR REPORTING
-- ============================================================================

-- Export complete election results for a specific election
SELECT 
    e.name as election_name,
    s.name as state_name,
    c.name as constituency_name,
    cand.name as candidate_name,
    p.short_name as party,
    r.votes_received,
    r.vote_percentage,
    r.position,
    CASE WHEN r.is_winner THEN 'Winner' ELSE 'Runner-up/Others' END as result_status,
    r.margin
FROM results r
JOIN elections e ON r.election_id = e.id
JOIN constituencies c ON r.constituency_id = c.id
JOIN states s ON c.state_id = s.id
JOIN candidates cand ON r.candidate_id = cand.id
JOIN parties p ON cand.party_id = p.id
WHERE e.year = 2024 AND e.election_type = 'Lok Sabha'
ORDER BY s.name, c.name, r.position;

-- ============================================================================
-- END OF SQL SAMPLES
-- ============================================================================

-- These queries demonstrate:
-- 1. Database schema design and creation
-- 2. Proper indexing for performance
-- 3. Basic CRUD operations
-- 4. Complex analytical queries used in the dashboard
-- 5. Data validation and quality checks
-- 6. Performance monitoring
-- 7. Advanced analytical insights
-- 8. Data export capabilities
--
-- All these queries are actively used in the Election Data Management System
-- to provide comprehensive election data analysis and insights.
