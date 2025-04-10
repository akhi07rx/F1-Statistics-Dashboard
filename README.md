# F1 Statistics Dashboard

A comprehensive command-line tool for analyzing Formula 1 race data using the FastF1 library.

## Overview

F1 Statistics Dashboard is a Python application that provides detailed statistics, visualizations, and analysis of Formula 1 race data. From viewing race schedules to comparing driver performances across seasons, this tool offers F1 fans and data enthusiasts a powerful way to explore the world of Formula 1 racing.

![F1 Dashboard Banner](https://via.placeholder.com/800x200?text=F1+Statistics+Dashboard)

## Features

### Race Information
- **Race Schedules**: View full season calendars for any F1 season
- **Race Results**: Get detailed results from specific races
- **Grand Prix Summaries**: Comprehensive information about each race including winners, podiums, fastest laps, and team points

### Driver Statistics
- **Podium Counts**: Track podium finishes for each driver in a season
- **DNF Analysis**: Analyze driver retirements and non-finishes
- **Driver Comparisons**: Compare two drivers' performances across multiple seasons

### Data Visualization
- **Driver Points Charts**: Visualize points distribution for each race
- **Performance Trends**: Track drivers and teams across a season

### Data Export
- **Season Details Export**: Export complete season data to CSV files
- **Historical Data Export**: Compile data across multiple seasons
- **Race Result Exports**: Save individual race results

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Required Libraries
```bash
pip install fastf1 pandas matplotlib tabulate
```

### Installing F1 Statistics Dashboard
```bash
# Clone the repository
git clone https://github.com/akhi07rx/f1-statistics-dashboard.git
cd f1-statistics-dashboard

# Install required dependencies
pip install -r requirements.txt
```

## Usage

### Interactive Menu
The easiest way to use the dashboard is through its interactive menu:

```bash
python f1_dashboard.py --menu
```

This opens a user-friendly interface organized into the following sections:
1. View Race Schedule
2. Race Results & Analysis
3. Driver Statistics
4. Season Analysis
5. Historical Data
6. Export Options

### Command-Line Arguments
You can also access specific features directly through command-line arguments:

```bash
# Display current season schedule
python f1_dashboard.py

# Show race schedule for a specific year
python f1_dashboard.py --schedule 2023

# Get race results and generate points chart
python f1_dashboard.py --results 2023 5

# Get fastest lap information
python f1_dashboard.py --fastest 2023 22

# Count podiums for each driver in a season
python f1_dashboard.py --podiums 2023

# Count DNFs for each driver in a season
python f1_dashboard.py --dnfs 2023

# Compare two drivers across seasons
python f1_dashboard.py --compare VER HAM 2021 2023

# Generate a Grand Prix summary
python f1_dashboard.py --summary 2023 22

# Export full season details to CSV
python f1_dashboard.py --export-season 2023

# Export race data for a date range
python f1_dashboard.py --export-history 2010 2023
```

### Help
For a full list of available commands:
```bash
python f1_dashboard.py --help
```

## Examples

### Viewing the Current Season Schedule
```python
from f1_dashboard import F1Dashboard

dashboard = F1Dashboard()
dashboard.display_race_schedule()
```

### Analyzing a Specific Grand Prix
```python
dashboard = F1Dashboard()
dashboard.grand_prix_summary(2023, 5)  # Monaco Grand Prix 2023
```

### Comparing Two Drivers
```python
dashboard = F1Dashboard()
dashboard.compare_drivers('VER', 'HAM', range(2021, 2024))  # Compare Verstappen and Hamilton from 2021-2023
```

### Exporting Full Season Data
```python
dashboard = F1Dashboard()
results, drivers, teams = dashboard.export_full_season_details(2023)
```

## Data Files

The dashboard creates the following data files:

| File | Description |
|------|-------------|
| `race{N}_results_{YEAR}.csv` | Results for a specific race |
| `race{N}_points_{YEAR}.png` | Points visualization for a specific race |
| `podiums_{YEAR}.csv` | Podium counts for a season |
| `dnfs_{YEAR}.csv` | DNF counts for a season |
| `full_season_{YEAR}_results.csv` | Complete race-by-race results for a season |
| `driver_standings_{YEAR}.csv` | Driver championship standings |
| `team_standings_{YEAR}.csv` | Team/constructor championship standings |
| `all_f1_races_{START}_to_{END}.csv` | Historical race data for a date range |

## Cache System

The dashboard uses FastF1's cache system to improve performance and reduce API calls. The cache is stored in the `f1_cache` directory, which is created automatically.

## Troubleshooting

### Common Issues

#### Data Loading Errors
```
Error getting race results for {year} round {race_round}: ...
```
Check your internet connection. The FastF1 library requires internet access to load data.

#### Missing Cache Directory
If you encounter this error:
```
NotADirectoryError: Cache directory does not exist!
```
The application should create this directory automatically, but you can manually create an `f1_cache` directory in the same location as the script.

#### Matplotlib Display Issues
If charts don't display properly, ensure you have a working display server or try exporting to image files instead.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) - The amazing library that makes this dashboard possible
- Formula 1 - For providing the data through their API
- All the contributors to Pandas, Matplotlib, and other libraries used in this project

---

*Disclaimer: This is an unofficial application and is not associated with, endorsed by, or affiliated with Formula 1 or the FIA Formula One World Championship.*