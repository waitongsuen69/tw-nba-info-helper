"""
Utility functions for NBA Game Data Scraper
"""

import pandas as pd
import os


def check_excel_data(filename=None):
    """
    Check and display the contents of the scraped NBA data

    Args:
        filename: Specific Excel file to check, or None for latest
    """
    if not filename:
        # Find the most recent Excel file
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and f.startswith('nba_game_data')]
        if not excel_files:
            print("No Excel files found")
            return
        filename = sorted(excel_files)[-1]

    print(f"Checking file: {filename}")
    print("=" * 60)

    # Read all sheets
    with pd.ExcelFile(filename) as xls:
        sheet_names = xls.sheet_names
        print(f"Found {len(sheet_names)} sheets in the Excel file:\n")

        for sheet_name in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Shape: {df.shape} (rows: {df.shape[0]}, columns: {df.shape[1]})")

            if not df.empty:
                print("\nColumn names:")
                print(list(df.columns))

                print("\nFirst few rows:")
                print(df.head(3))

                # Show summary for player stats
                if 'Player Stats' in sheet_name and df.shape[0] > 0:
                    print("\nSample player data:")
                    # Try to find columns with player names and points
                    for col in df.columns:
                        if any(keyword in str(col).lower() for keyword in ['name', 'player', '球員']):
                            print(f"Players found: {df[col].nunique()} unique players")
                            break

                # Show team statistics summary
                if sheet_name == 'Team Season Statistics':
                    print("\nStatistics included:")
                    if 'Statistic' in df.columns:
                        for stat in df['Statistic'].tolist():
                            print(f"  • {stat}")

            print("-" * 60)


def verify_sheets(filename=None):
    """
    Verify the sheet names in the generated Excel file

    Args:
        filename: Specific Excel file to check, or None for latest
    """
    if not filename:
        # Find the most recent Excel file
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and f.startswith('nba_game_data')]
        if not excel_files:
            print("No Excel files found")
            return
        filename = sorted(excel_files)[-1]

    print(f"Checking file: {filename}")
    print("=" * 50)

    # Read and display sheet names
    with pd.ExcelFile(filename) as xls:
        sheet_names = xls.sheet_names
        print(f"Found {len(sheet_names)} sheets:\n")

        for i, sheet_name in enumerate(sheet_names, 1):
            df = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"{i:2}. {sheet_name:<35} ({df.shape[0]} rows, {df.shape[1]} columns)")

        # Check for key sheets
        print("\n" + "=" * 50)
        print("Sheet Structure Verification:")

        expected_sheets = ['Player Stats', 'Quarter Scores', 'Team Season Statistics']
        for sheet in expected_sheets:
            if sheet in sheet_names:
                print(f"✅ {sheet} sheet found")
            else:
                print(f"❌ {sheet} sheet missing")

        # Check for team player sheets
        team_sheets = [s for s in sheet_names if '_Players' in s]
        if team_sheets:
            print(f"✅ Found {len(team_sheets)} team player sheets:")
            for sheet in team_sheets:
                print(f"   - {sheet}")
        else:
            print("❌ No team player sheets found")