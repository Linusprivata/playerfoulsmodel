"""DuckDB schema definitions for player fouls data."""

PLAYER_MATCH_STATS_SCHEMA = """
CREATE TABLE IF NOT EXISTS player_match_stats (
    -- Identifiers
    player_id VARCHAR,
    player_name VARCHAR,
    match_id VARCHAR,
    
    -- FBref columns (35 total - 28 original + 7 new)
    date DATE,
    competition VARCHAR,
    venue VARCHAR,
    result VARCHAR,
    opponent VARCHAR,
    starting BOOLEAN,  -- NEW: Whether player started
    position VARCHAR,
    minutes INTEGER,
    fouls INTEGER,
    fouled INTEGER,
    tackles INTEGER,
    tackles_def_3rd INTEGER,
    tackles_mid_3rd INTEGER,
    tackles_att_3rd INTEGER,
    challenges INTEGER,
    take_ons INTEGER,
    team_fouls INTEGER,  -- NEW: Total fouls by player's team
    team_fouled INTEGER,  -- NEW: Total times player's team was fouled
    team_possession_pct FLOAT,  -- NEW: Team's possession percentage
    opponent_possession_pct FLOAT,  -- NEW: Opponent's possession percentage
    
    -- Sofascore columns (4)
    odds_winning FLOAT,
    heatmap JSON,  -- Store as JSON
    nearest_opponents JSON,  -- List of player IDs/names
    nearest_opponents_fouled JSON,  -- List of foul counts
    
    -- Whoscored columns (7)
    foul_position JSON,  -- Coordinates
    team_left_attack_pct FLOAT,
    team_mid_attack_pct FLOAT,
    team_right_attack_pct FLOAT,
    opponent_left_attack_pct FLOAT,
    opponent_mid_attack_pct FLOAT,
    opponent_right_attack_pct FLOAT,
    
    -- Metadata
    referee_id VARCHAR,
    referee_name VARCHAR,  -- NEW: Match referee name
    attendance INTEGER,  -- NEW: Match attendance
    comments TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Primary key
    PRIMARY KEY (player_id, match_id)
);
"""

PLAYERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    player_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    current_team VARCHAR,
    nationality VARCHAR,
    position VARCHAR,
    birth_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

TEAMS_SCHEMA = """
CREATE TABLE IF NOT EXISTS teams (
    team_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    league VARCHAR,
    country VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

REFEREES_SCHEMA = """
CREATE TABLE IF NOT EXISTS referees (
    referee_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    avg_fouls_per_game FLOAT,
    total_games INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

MATCHES_SCHEMA = """
CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR PRIMARY KEY,
    date DATE NOT NULL,
    competition VARCHAR,
    home_team_id VARCHAR,
    away_team_id VARCHAR,
    home_score INTEGER,
    away_score INTEGER,
    venue VARCHAR,
    attendance INTEGER,
    referee_id VARCHAR,
    fbref_url VARCHAR,
    sofascore_url VARCHAR,
    whoscored_url VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

ALL_SCHEMAS = [
    PLAYERS_SCHEMA,
    TEAMS_SCHEMA,
    REFEREES_SCHEMA,
    MATCHES_SCHEMA,
    PLAYER_MATCH_STATS_SCHEMA
]