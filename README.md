# NBA Game Data Scraper

A Python web scraper that extracts NBA game data from tw-nba.udn.com and saves it to Excel format.

## Features

- Scrapes comprehensive NBA game statistics
- Extracts player stats, team stats, quarter scores
- Automatically identifies team names and formats them as "Chinese(English)"
- Saves data to organized Excel sheets with proper naming
- Command-line interface with URL parameter support
- Clean code structure with separated modules

## Project Structure

```
nba_spider/
├── main.py              # Main entry point
├── src/
│   ├── __init__.py      # Package initialization
│   ├── scraper.py       # NBAGameScraper class
│   └── utils.py         # Utility functions
├── output_excel/        # Output directory for Excel files
│   └── team1_team2_date.xlsx  # Generated files
├── venv/                # Virtual environment
└── README.md            # Documentation
```

## Installation

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install required packages:
```bash
pip install requests beautifulsoup4 pandas openpyxl lxml
```

## Usage

### Basic Usage
```bash
python main.py [URL]
```

### Examples
```bash
# Scrape a specific game
python main.py https://tw-nba.udn.com/nba/standings_game/534867d1-8ef1-4929-b32c-4f766f159017

# Using --url flag
python main.py --url https://tw-nba.udn.com/nba/standings_game/[game-id]

# Custom output filename
python main.py [URL] --output my_game_data.xlsx

# Show help
python main.py --help
```

### Running without URL
If no URL is provided, the script will prompt you to either:
- Enter a URL manually
- Use the default test URL

## Output

The scraper saves Excel files to the `output_excel` directory with the naming format:
- `team1_team2_YYYYMMDD_HHMMSS.xlsx`
- Example: `塞爾蒂克_籃網_20251119_223641.xlsx`

Each Excel file contains the following sheets:

1. **Player Stats** - Combined player statistics from both teams
2. **Quarter Scores** - Quarter-by-quarter scores for both teams
3. **Team1(English)_Players** - First team's detailed player stats (e.g., "塞爾蒂克(Celtics)_Players")
4. **Team2(English)_Players** - Second team's detailed player stats (e.g., "籃網(Nets)_Players")
5. **Team Season Statistics** - Consolidated season statistics for both teams including:
   - Points per Game with league rankings
   - Assists per Game with league rankings
   - Rebounds per Game with league rankings
   - Blocks per Game with league rankings
   - Steals per Game with league rankings
   - Field Goal % with league rankings
   - 3-Point % with league rankings
   - Free Throw % with league rankings
   - Turnovers per Game with league rankings

## Data Extracted

### Player Statistics
- Position, Playing time
- Points, Rebounds (offensive/defensive/total)
- Assists, Steals, Blocks
- Shooting stats (FG, 3PT, FT)
- Turnovers, Fouls, +/- rating

### Team Statistics
- Season averages with league rankings
- Quarter-by-quarter scoring
- Team comparison stats

## Team Name Mapping

The scraper automatically maps Chinese team names to English:
- 塞爾蒂克 → Celtics
- 籃網 → Nets
- 湖人 → Lakers
- 勇士 → Warriors
- (and all 30 NBA teams)

## Files

- `main.py` - Main entry point script
- `src/scraper.py` - NBAGameScraper class implementation
- `src/utils.py` - Utility functions for data verification
- `src/__init__.py` - Package initialization

## Troubleshooting

If you encounter issues:
1. Ensure you have activated the virtual environment
2. Check that all required packages are installed
3. Verify the URL is valid and accessible
4. Check your internet connection

## Example Output

After successful scraping:
```
Starting NBA Game Scraper...
==================================================
URL: https://tw-nba.udn.com/nba/standings_game/...
Fetching data from: https://tw-nba.udn.com/...
Found 42 player statistics
Consolidated 18 team statistics entries
Data saved to output_excel/塞爾蒂克_籃網_20251119_223641.xlsx
Team names found: ['塞爾蒂克(Celtics)', '籃網(Nets)']
==================================================
Scraping completed successfully!
Total player stats collected: 42
Total tables found: 12
```