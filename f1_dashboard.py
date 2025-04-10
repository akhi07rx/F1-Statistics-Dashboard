"""
F1 Statistics Dashboard - Interactive command-line tool for F1 race data analysis
"""

import argparse
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
from datetime import datetime
import os
import sys
import time


def create_cache_directory():
    """Create cache directory if it doesn't exist"""
    cache_dir = 'f1_cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        print(f"Created cache directory: {cache_dir}")
    return cache_dir


# Create cache directory and configure fastf1 cache
cache_dir = create_cache_directory()
fastf1.Cache.enable_cache(cache_dir)


class F1Dashboard:
    def __init__(self):
        self.current_year = datetime.now().year

    def get_race_schedule(self, year=None):
        """Get and display the F1 race schedule for a given year"""
        year = year or self.current_year
        try:
            race_schedule = fastf1.get_event_schedule(year)
            return race_schedule
        except Exception as e:
            print(f"Error getting race schedule for {year}: {e}")
            return None

    def display_race_schedule(self, year=None):
        """Display the F1 race schedule in a formatted table"""
        race_schedule = self.get_race_schedule(year)
        if race_schedule is not None:
            # Display key schedule information
            print(f"\n=== F1 {year or self.current_year} Race Calendar ===\n")
            schedule_display = race_schedule[['RoundNumber', 'Country', 'Location',
                                             'EventName', 'EventDate', 'Session5Date']]
            print(tabulate(schedule_display, headers='keys', tablefmt='grid'))

            # Show upcoming race
            try:
                upcoming = race_schedule[race_schedule['EventDate'] > pd.Timestamp(
                    datetime.now())].head(1)
                if not upcoming.empty:
                    print("\n=== Next Upcoming Race ===\n")
                    print(tabulate(upcoming[['Country', 'Location', 'EventName', 'EventDate']],
                                   headers='keys', tablefmt='simple'))
            except Exception as e:
                print(f"Error finding upcoming races: {e}")

            return race_schedule

    def get_race_results(self, year, race_round):
        """Get race results for a specific race"""
        try:
            session = fastf1.get_session(year, race_round, 'R')
            session.load()
            return session
        except Exception as e:
            print(
                f"Error getting race results for {year} round {race_round}: {e}")
            return None

    def display_race_results(self, year, race_round):
        """Display race results with points"""
        session = self.get_race_results(year, race_round)
        if session is not None:
            results = session.results.loc[:, ['DriverNumber', 'Abbreviation', 'FullName',
                                              'TeamName', 'Position', 'ClassifiedPosition',
                                              'Points', 'Status']]

            # Sort by classified position and handle non-numeric values
            results['ClassifiedPosition'] = pd.to_numeric(
                results['ClassifiedPosition'], errors='coerce')
            results = results.sort_values(by='ClassifiedPosition')

            print(
                f"\n=== Race Results: {year} Round {race_round} ({session.event['EventName']}) ===\n")
            print(tabulate(results, headers='keys', tablefmt='grid'))

            # Save results to CSV
            csv_filename = f"race{race_round}_results_{year}.csv"
            results.to_csv(csv_filename, index=False)
            print(f"\nResults saved to {csv_filename}")

            return results

    def plot_driver_points(self, results, year, race_round):
        """Plot driver points for a race"""
        if results is not None:
            plt.figure(figsize=(12, 6))

            # Sort by points in descending order
            results_sorted = results.sort_values(by='Points', ascending=False)

            # Create bar chart
            plt.bar(results_sorted['Abbreviation'], results_sorted['Points'])
            plt.title(f"Driver Points for Race {race_round} ({year})")
            plt.xlabel("Driver")
            plt.ylabel("Points")
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Save and show plot
            plot_filename = f"race{race_round}_points_{year}.png"
            plt.savefig(plot_filename)
            plt.show()
            print(f"\nPoints chart saved to {plot_filename}")

    def get_fastest_lap(self, year, race_round):
        """Get fastest lap information for a race"""
        session = self.get_race_results(year, race_round)
        if session is not None:
            try:
                fastest = session.laps.pick_fastest()
                print(f"\n=== Fastest Lap: {year} Round {race_round} ===\n")
                print(f"Driver: {fastest['Driver']}")
                print(f"Team: {fastest['Team']}")
                print(f"Lap Time: {fastest['LapTime']}")
                print(f"Lap Number: {fastest['LapNumber']}")
                print(f"Compound: {fastest['Compound']}")

                return fastest
            except Exception as e:
                print(f"Error getting fastest lap: {e}")
                return None

    def count_podiums(self, year):
        """Count podiums for each driver in a season"""
        podium_counts = {}

        race_schedule = self.get_race_schedule(year)
        if race_schedule is None:
            return

        # Get completed races
        completed_rounds = race_schedule[race_schedule['EventDate'] < pd.Timestamp(
            datetime.now())]['RoundNumber'].tolist()

        print(f"\n=== Podium Counts for {year} Season ===\n")

        for round_num in completed_rounds:
            try:
                session = fastf1.get_session(year, round_num, 'R')
                session.load()

                # Extract top 3 finishers
                podium_drivers = session.results.sort_values(
                    'Position').head(3)['Abbreviation'].tolist()

                # Update podium counts
                for driver in podium_drivers:
                    if driver in podium_counts:
                        podium_counts[driver] += 1
                    else:
                        podium_counts[driver] = 1

            except Exception as e:
                print(f"Error processing round {round_num}: {e}")
                continue

        # Display podium counts
        sorted_counts = sorted(podium_counts.items(),
                               key=lambda x: x[1], reverse=True)
        podium_df = pd.DataFrame(sorted_counts, columns=['Driver', 'Podiums'])
        print(tabulate(podium_df, headers='keys', tablefmt='grid'))

        return podium_df

    def count_dnfs(self, year):
        """Count DNFs for each driver in a season"""
        dnf_counts = {}

        race_schedule = self.get_race_schedule(year)
        if race_schedule is None:
            return

        # Get completed races
        completed_rounds = race_schedule[race_schedule['EventDate'] < pd.Timestamp(
            datetime.now())]['RoundNumber'].tolist()

        print(f"\n=== DNF Counts for {year} Season ===\n")

        for round_num in completed_rounds:
            try:
                session = fastf1.get_session(year, round_num, 'R')
                session.load()

                # Extract DNF drivers (those with non-finished status)
                dnf_drivers = session.results[~session.results['Status'].isin(
                    ['Finished'])]['Abbreviation'].tolist()

                # Update DNF counts
                for driver in dnf_drivers:
                    if driver in dnf_counts:
                        dnf_counts[driver] += 1
                    else:
                        dnf_counts[driver] = 1

            except Exception as e:
                print(f"Error processing round {round_num}: {e}")
                continue

        # Display DNF counts
        sorted_counts = sorted(
            dnf_counts.items(), key=lambda x: x[1], reverse=True)
        dnf_df = pd.DataFrame(sorted_counts, columns=['Driver', 'DNFs'])
        print(tabulate(dnf_df, headers='keys', tablefmt='grid'))

        return dnf_df

    def compare_drivers(self, driver1, driver2, years):
        """Compare performance of two drivers across seasons"""
        print(f"\n=== Driver Comparison: {driver1} vs {driver2} ===\n")

        comparison_data = []

        for year in years:
            try:
                # Get season results for both drivers
                driver1_points = 0
                driver2_points = 0
                driver1_wins = 0
                driver2_wins = 0

                race_schedule = self.get_race_schedule(year)
                if race_schedule is None:
                    continue

                # Get completed races
                completed_rounds = race_schedule[race_schedule['EventDate'] < pd.Timestamp(
                    datetime.now())]['RoundNumber'].tolist()

                for round_num in completed_rounds:
                    try:
                        session = fastf1.get_session(year, round_num, 'R')
                        session.load()

                        # Get results for both drivers
                        driver1_result = session.results[session.results['Abbreviation'] == driver1]
                        driver2_result = session.results[session.results['Abbreviation'] == driver2]

                        # Add points
                        if not driver1_result.empty:
                            driver1_points += driver1_result['Points'].values[0]
                            if driver1_result['Position'].values[0] == 1:
                                driver1_wins += 1

                        if not driver2_result.empty:
                            driver2_points += driver2_result['Points'].values[0]
                            if driver2_result['Position'].values[0] == 1:
                                driver2_wins += 1

                    except Exception as e:
                        print(f"Error processing round {round_num}: {e}")
                        continue

                # Add season data to comparison
                comparison_data.append({
                    'Year': year,
                    f'{driver1} Points': driver1_points,
                    f'{driver2} Points': driver2_points,
                    f'{driver1} Wins': driver1_wins,
                    f'{driver2} Wins': driver2_wins
                })

            except Exception as e:
                print(f"Error processing year {year}: {e}")
                continue

        # Display comparison
        comparison_df = pd.DataFrame(comparison_data)
        print(tabulate(comparison_df, headers='keys', tablefmt='grid'))

        return comparison_df

    def grand_prix_summary(self, year, race_round):
        """Generate a comprehensive summary of a Grand Prix"""
        session = self.get_race_results(year, race_round)
        if session is None:
            return

        print(f"\n=== Grand Prix Summary: {year} Round {race_round} ===\n")

        # Basic event info
        print(f"Event: {session.event['EventName']}")
        print(
            f"Location: {session.event['Location']}, {session.event['Country']}")
        print(f"Date: {session.event['EventDate'].strftime('%Y-%m-%d')}")
        print(f"Circuit: {session.event['CircuitName']}")

        # Winner
        try:
            winner = session.results.sort_values('Position').iloc[0]
            print(
                f"\nWinner: {winner['FullName']} ({winner['Abbreviation']}) - {winner['TeamName']}")
            print(f"Time: {winner['Time']}")
        except Exception as e:
            print(f"Error getting winner info: {e}")

        # Podium
        try:
            podium = session.results.sort_values('Position').head(3)
            print("\nPodium:")
            for i, (_, driver) in enumerate(podium.iterrows()):
                print(
                    f"{i+1}. {driver['FullName']} ({driver['Abbreviation']}) - {driver['TeamName']}")
        except Exception as e:
            print(f"Error getting podium info: {e}")

        # Fastest lap
        try:
            fastest = session.laps.pick_fastest()
            fastest_driver = session.get_driver(fastest['DriverNumber'])
            print(
                f"\nFastest Lap: {fastest_driver['Abbreviation']} - {fastest['LapTime']} (Lap {fastest['LapNumber']})")
        except Exception as e:
            print(f"Error getting fastest lap info: {e}")

        # Points by team
        try:
            team_points = session.results.groupby(
                'TeamName')['Points'].sum().sort_values(ascending=False)
            print("\nTeam Points in this Race:")
            print(tabulate(pd.DataFrame(team_points).reset_index(),
                  headers=['Team', 'Points'], tablefmt='simple'))
        except Exception as e:
            print(f"Error getting team points: {e}")

        # Notable retirements
        try:
            retirements = session.results[session.results['Status']
                                          != 'Finished']
            if not retirements.empty:
                print("\nRetirements:")
                for _, driver in retirements.iterrows():
                    print(
                        f"- {driver['FullName']} ({driver['Abbreviation']}) - {driver['Status']}")
        except Exception as e:
            print(f"Error getting retirement info: {e}")

        # Return session for further processing
        return session

    def export_full_season_details(self, year):
        """Export full details for a season to CSV"""
        race_schedule = self.get_race_schedule(year)
        if race_schedule is None:
            return

        print(f"\n=== Exporting Full Season Details for {year} ===\n")

        # Initialize data structures
        all_results = []
        driver_points = {}
        team_points = {}

        # Get completed races
        completed_rounds = race_schedule[race_schedule['EventDate'] < pd.Timestamp(
            datetime.now())]['RoundNumber'].tolist()

        # Process each race
        for round_num in completed_rounds:
            try:
                print(f"Processing round {round_num}...")
                session = fastf1.get_session(year, round_num, 'R')
                session.load()

                race_name = session.event['EventName']

                # Process each driver's result
                for _, result in session.results.iterrows():
                    driver = result['Abbreviation']
                    team = result['TeamName']
                    points = result['Points']

                    # Update season points
                    if driver not in driver_points:
                        driver_points[driver] = 0
                    driver_points[driver] += points

                    if team not in team_points:
                        team_points[team] = 0
                    team_points[team] += points

                    # Add to all results
                    all_results.append({
                        'Round': round_num,
                        'Race': race_name,
                        'Driver': driver,
                        'FullName': result['FullName'],
                        'Team': team,
                        'Position': result['Position'],
                        'Points': points,
                        'Status': result['Status'],
                        'CumulativePoints': driver_points[driver]
                    })

            except Exception as e:
                print(f"Error processing round {round_num}: {e}")
                continue

        # Create and save results DataFrame
        results_df = pd.DataFrame(all_results)
        results_filename = f"full_season_{year}_results.csv"
        results_df.to_csv(results_filename, index=False)
        print(f"Full season results saved to {results_filename}")

        # Create and save driver standings
        driver_standings = pd.DataFrame(sorted(driver_points.items(), key=lambda x: x[1], reverse=True),
                                        columns=['Driver', 'Points'])
        driver_filename = f"driver_standings_{year}.csv"
        driver_standings.to_csv(driver_filename, index=False)
        print(f"Driver standings saved to {driver_filename}")

        # Create and save team standings
        team_standings = pd.DataFrame(sorted(team_points.items(), key=lambda x: x[1], reverse=True),
                                      columns=['Team', 'Points'])
        team_filename = f"team_standings_{year}.csv"
        team_standings.to_csv(team_filename, index=False)
        print(f"Team standings saved to {team_filename}")

        return results_df, driver_standings, team_standings

    def export_all_time_race_data(self, start_year, end_year=None):
        """Export race data from first race to current"""
        end_year = end_year or self.current_year

        print(
            f"\n=== Exporting All Race Data from {start_year} to {end_year} ===\n")
        print("This may take a while depending on the date range...")

        # Initialize data structures
        all_races = []

        # Process each year
        for year in range(start_year, end_year + 1):
            try:
                print(f"Processing year {year}...")
                race_schedule = self.get_race_schedule(year)
                if race_schedule is None:
                    continue

                # Get completed races for this year
                completed_rounds = race_schedule[race_schedule['EventDate'] < pd.Timestamp(
                    datetime.now())]['RoundNumber'].tolist()

                # Process each race
                for round_num in completed_rounds:
                    try:
                        session = fastf1.get_session(year, round_num, 'R')
                        session.load()

                        # Basic race info
                        race_info = {
                            'Year': year,
                            'Round': round_num,
                            'Name': session.event['EventName'],
                            'Date': session.event['EventDate'],
                            'Circuit': session.event['CircuitName'],
                            'Country': session.event['Country']
                        }

                        # Winner info
                        winner = session.results.sort_values(
                            'Position').iloc[0]
                        race_info['Winner'] = winner['FullName']
                        race_info['WinningTeam'] = winner['TeamName']

                        # Fastest lap
                        try:
                            fastest = session.laps.pick_fastest()
                            race_info['FastestLapDriver'] = fastest['Driver']
                            race_info['FastestLapTime'] = str(
                                fastest['LapTime'])
                        except:
                            race_info['FastestLapDriver'] = 'N/A'
                            race_info['FastestLapTime'] = 'N/A'

                        all_races.append(race_info)

                    except Exception as e:
                        print(
                            f"Error processing {year} round {round_num}: {e}")
                        continue

            except Exception as e:
                print(f"Error processing year {year}: {e}")
                continue

        # Create and save all-time race data
        races_df = pd.DataFrame(all_races)
        filename = f"all_f1_races_{start_year}_to_{end_year}.csv"
        races_df.to_csv(filename, index=False)
        print(f"\nAll race data saved to {filename}")

        return races_df


def display_intro():
    """Display introduction message"""
    print("\n" + "=" * 80)
    print("                          F1 STATISTICS DASHBOARD")
    print("=" * 80)
    print("\nWelcome to the Formula 1 Statistics Dashboard!")
    print("This tool provides comprehensive F1 statistics and analysis capabilities.")
    print("\nCreated by akhi07rx with the fastf1 Python library")
    print("=" * 80 + "\n")


def display_menu():
    """Display interactive menu"""
    print("\nMAIN MENU")
    print("-" * 50)
    print("1. View Race Schedule")
    print("2. Race Results & Analysis")
    print("3. Driver Statistics")
    print("4. Season Analysis")
    print("5. Historical Data")
    print("6. Export Options")
    print("0. Exit")
    print("-" * 50)


def get_valid_input(prompt, valid_range=None):
    """Get valid input from user with validation"""
    while True:
        try:
            value = input(prompt)
            if valid_range is None:
                return value
            value = int(value)
            if valid_range[0] <= value <= valid_range[1]:
                return value
            print(
                f"Please enter a number between {valid_range[0]} and {valid_range[1]}")
        except ValueError:
            print("Please enter a valid number")


def interactive_menu():
    """Run interactive menu system"""
    dashboard = F1Dashboard()
    display_intro()

    while True:
        display_menu()
        choice = get_valid_input("Enter your choice (0-6): ", (0, 6))

        if choice == 0:
            print("\nThank you for using the F1 Statistics Dashboard. Goodbye!")
            break

        elif choice == 1:
            print("\nVIEW RACE SCHEDULE")
            print("-" * 50)
            print("1. Current Season Schedule")
            print("2. Specific Year Schedule")
            print("3. Return to Main Menu")
            subchoice = get_valid_input("Enter your choice (1-3): ", (1, 3))

            if subchoice == 1:
                dashboard.display_race_schedule()
            elif subchoice == 2:
                year = get_valid_input(
                    "Enter year (1950-2025): ", (1950, 2025))
                dashboard.display_race_schedule(year)

        elif choice == 2:
            print("\nRACE RESULTS & ANALYSIS")
            print("-" * 50)
            print("1. Race Results")
            print("2. Fastest Lap Information")
            print("3. Grand Prix Summary")
            print("4. Return to Main Menu")
            subchoice = get_valid_input("Enter your choice (1-4): ", (1, 4))

            if subchoice in [1, 2, 3]:
                year = get_valid_input(
                    "Enter year (1950-2025): ", (1950, 2025))
                race_round = get_valid_input(
                    "Enter race round number: ", (1, 30))

                if subchoice == 1:
                    results = dashboard.display_race_results(year, race_round)
                    plot = get_valid_input("Generate points plot? (y/n): ")
                    if plot.lower() == 'y':
                        dashboard.plot_driver_points(results, year, race_round)
                elif subchoice == 2:
                    dashboard.get_fastest_lap(year, race_round)
                elif subchoice == 3:
                    dashboard.grand_prix_summary(year, race_round)

        elif choice == 3:
            print("\nDRIVER STATISTICS")
            print("-" * 50)
            print("1. Count Podiums for Season")
            print("2. Count DNFs for Season")
            print("3. Compare Two Drivers")
            print("4. Return to Main Menu")
            subchoice = get_valid_input("Enter your choice (1-4): ", (1, 4))

            if subchoice == 1:
                year = get_valid_input(
                    "Enter year (1950-2025): ", (1950, 2025))
                podium_data = dashboard.count_podiums(year)
                save = get_valid_input("Save to CSV? (y/n): ")
                if save.lower() == 'y' and podium_data is not None:
                    podium_data.to_csv(f"podiums_{year}.csv", index=False)
                    print(f"Saved to podiums_{year}.csv")

            elif subchoice == 2:
                year = get_valid_input(
                    "Enter year (1950-2025): ", (1950, 2025))
                dnf_data = dashboard.count_dnfs(year)
                save = get_valid_input("Save to CSV? (y/n): ")
                if save.lower() == 'y' and dnf_data is not None:
                    dnf_data.to_csv(f"dnfs_{year}.csv", index=False)
                    print(f"Saved to dnfs_{year}.csv")

            elif subchoice == 3:
                driver1 = get_valid_input(
                    "Enter first driver abbreviation (e.g., HAM): ")
                driver2 = get_valid_input(
                    "Enter second driver abbreviation (e.g., VER): ")
                start_year = get_valid_input(
                    "Enter start year (1950-2025): ", (1950, 2025))
                end_year = get_valid_input(
                    "Enter end year (1950-2025): ", (1950, 2025))
                comparison = dashboard.compare_drivers(
                    driver1.upper(), driver2.upper(), range(start_year, end_year + 1))
                save = get_valid_input("Save to CSV? (y/n): ")
                if save.lower() == 'y' and comparison is not None:
                    comparison.to_csv(
                        f"comparison_{driver1}_{driver2}_{start_year}_{end_year}.csv", index=False)
                    print(
                        f"Saved to comparison_{driver1}_{driver2}_{start_year}_{end_year}.csv")

        elif choice == 4:
            print("\nSEASON ANALYSIS")
            print("-" * 50)
            print("1. Full Season Details")
            print("2. Return to Main Menu")
            subchoice = get_valid_input("Enter your choice (1-2): ", (1, 2))

            if subchoice == 1:
                year = get_valid_input(
                    "Enter year (1950-2025): ", (1950, 2025))
                dashboard.export_full_season_details(year)

        elif choice == 5:
            print("\nHISTORICAL DATA")
            print("-" * 50)
            print("1. Export All Race Data for Date Range")
            print("2. Return to Main Menu")
            subchoice = get_valid_input("Enter your choice (1-2): ", (1, 2))

            if subchoice == 1:
                start_year = get_valid_input(
                    "Enter start year (1950-2025): ", (1950, 2025))
                end_year = get_valid_input(
                    "Enter end year (1950-2025): ", (1950, 2025))
                if start_year > end_year:
                    start_year, end_year = end_year, start_year
                dashboard.export_all_time_race_data(start_year, end_year)

        elif choice == 6:
            print("\nEXPORT OPTIONS")
            print("-" * 50)
            print("1. Export Full Season Details")
            print("2. Export All-Time Race Winners")
            print("3. Return to Main Menu")
            subchoice = get_valid_input("Enter your choice (1-3): ", (1, 3))

            if subchoice == 1:
                year = get_valid_input(
                    "Enter year (1950-2025): ", (1950, 2025))
                dashboard.export_full_season_details(year)
            elif subchoice == 2:
                start_year = get_valid_input(
                    "Enter start year (1950-2025): ", (1950, 2025))
                end_year = get_valid_input(
                    "Enter end year (or press Enter for current year): ")
                if end_year:
                    end_year = int(end_year)
                else:
                    end_year = None
                dashboard.export_all_time_race_data(start_year, end_year)

        # Pause before showing menu again
        input("\nPress Enter to continue...")


def main():
    parser = argparse.ArgumentParser(description="F1 Statistics Dashboard")
    parser.add_argument("--menu", action="store_true",
                        help="Start interactive menu")
    parser.add_argument("--schedule", type=int, nargs='?', const=datetime.now().year,
                        help="Display race schedule for a given year (defaults to current year)")
    parser.add_argument("--results", type=int, nargs=2, metavar=('YEAR', 'ROUND'),
                        help="Display race results (e.g. --results 2023 5)")
    parser.add_argument("--fastest", type=int, nargs=2, metavar=('YEAR', 'ROUND'),
                        help="Display fastest lap for a race")
    parser.add_argument("--podiums", type=int,
                        help="Count podiums for each driver in a season")
    parser.add_argument("--dnfs", type=int,
                        help="Count DNFs for each driver in a season")
    parser.add_argument("--compare", nargs=4, metavar=('DRIVER1', 'DRIVER2', 'START_YEAR', 'END_YEAR'),
                        help="Compare two drivers across seasons (e.g. --compare VER HAM 2021 2023)")
    parser.add_argument("--summary", type=int, nargs=2, metavar=('YEAR', 'ROUND'),
                        help="Generate Grand Prix summary (e.g. --summary 2023 5)")
    parser.add_argument("--export-season", type=int, metavar='YEAR',
                        help="Export full season details to CSV (e.g. --export-season 2023)")
    parser.add_argument("--export-history", type=int, nargs=2, metavar=('START_YEAR', 'END_YEAR'),
                        help="Export race data for a date range (e.g. --export-history 2010 2023)")

    args = parser.parse_args()

    dashboard = F1Dashboard()

    # If no arguments provided or --menu specified, run interactive menu
    if len(sys.argv) == 1 or args.menu:
        interactive_menu()
        return

    # Execute the requested action
    if args.schedule is not None:
        dashboard.display_race_schedule(args.schedule)

    elif args.results is not None:
        year, race_round = args.results
        results = dashboard.display_race_results(year, race_round)
        dashboard.plot_driver_points(results, year, race_round)

    elif args.fastest is not None:
        year, race_round = args.fastest
        dashboard.get_fastest_lap(year, race_round)

    elif args.podiums is not None:
        dashboard.count_podiums(args.podiums)

    elif args.dnfs is not None:
        dashboard.count_dnfs(args.dnfs)

    elif args.compare is not None:
        driver1, driver2, start_year, end_year = args.compare
        years = range(int(start_year), int(end_year) + 1)
        dashboard.compare_drivers(driver1, driver2, years)

    elif args.summary is not None:
        year, race_round = args.summary
        dashboard.grand_prix_summary(year, race_round)

    elif args.export_season is not None:
        dashboard.export_full_season_details(args.export_season)

    elif args.export_history is not None:
        start_year, end_year = args.export_history
        dashboard.export_all_time_race_data(start_year, end_year)

    else:
        # Default: display current season schedule
        print("Use --menu for interactive mode or --help to see available commands")
        dashboard.display_race_schedule()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("If this is related to data access, please check your internet connection.")
