# Player Fouls Prediction Model

A machine learning system for predicting player fouls using multi-source football data.

## Overview

This project collects and analyzes football match data from multiple sources (FBref, Sofascore, Whoscored) to build predictive models for player fouls. The system stores ~400 games for ~1000 players in a DuckDB database for fast local querying.

## Project Status

### ✅ Completed
- Project structure and dependencies setup
- DuckDB database schema design
- FBref scraper implementation using ScraperFC
- Database connection and initialization
- Sample data collection script

### 🚧 In Progress
- Testing single row data collection from FBref
- Data validation and quality checks

### 📋 Upcoming
- Sofascore integration (odds, heatmaps, nearest opponents)
- Whoscored integration (foul positions, attack percentages)
- Bulk data collection for all players
- ML model development

## Setup

### Prerequisites
- Python 3.11+
- ~100GB disk space for full dataset

### Installation

1. Clone the repository:
```bash
cd playerfoulsmodel
```

2. Run the setup script:
```bash
python setup.py
```

This will:
- Create a virtual environment
- Install all dependencies
- Initialize the DuckDB database
- Create a .env file from the template

### Manual Setup (if setup.py fails)

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Initialize database
python -c "from src.data.database import init_database; init_database()"
```

## Usage

### Collect Sample Data

To test the system with a single match:

```bash
python scripts/collect_sample.py
```

You'll need:
- A valid FBref match URL (e.g., `https://fbref.com/en/matches/...`)
- The exact player name as it appears on FBref

### Data Sources

The system collects 35 columns of data per player per match:

#### FBref (28 columns)
- Match details: date, competition, venue, result, opponent
- Player stats: position, minutes, fouls, fouled, tackles, etc.
- Team stats: possession, team fouls/fouled

#### Sofascore (4 columns)
- Betting odds
- Player heatmaps
- Nearest opponents and their foul counts

#### Whoscored (7 columns)
- Foul position coordinates
- Team attack distribution percentages

## Project Structure

```
playerfoulsmodel/
├── data/               # Data storage
│   ├── duckdb/        # DuckDB database files
│   ├── raw/           # Raw scraped data
│   └── samples/       # Sample test data
├── src/               # Source code
│   ├── scrapers/      # Web scrapers for each source
│   ├── data/          # Database and data processing
│   ├── models/        # ML models
│   └── query/         # Query API
├── scripts/           # Utility scripts
├── notebooks/         # Jupyter notebooks
└── tests/            # Unit tests
```

## Database Schema

The main table `player_match_stats` contains all 35 columns per match:
- Player and match identifiers
- All statistics from FBref, Sofascore, and Whoscored
- Metadata (referee, attendance, scrape timestamp)

Supporting tables:
- `players`: Player information
- `teams`: Team information
- `referees`: Referee statistics
- `matches`: Match metadata

## Development

### Adding New Scrapers

1. Create a new scraper in `src/scrapers/`
2. Inherit from `BaseScraper`
3. Implement `scrape_match()` and `validate_data()`
4. Add to the data collection pipeline

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Type checking
mypy src/
```

## Next Steps

1. **Complete FBref Testing**: Verify all 28 columns populate correctly
2. **Add Sofascore**: Integrate odds and heatmap data
3. **Add Whoscored**: Integrate foul positions and attack patterns
4. **Bulk Collection**: Scale to 1000 players
5. **ML Development**: Build prediction models

## License

[Add license information] 
