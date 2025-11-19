#!/usr/bin/env python3
"""
NBA Game Data Scraper - Main Entry Point

Usage:
    python main.py [URL]
    python main.py --url [URL]
    python main.py --help
"""

import sys
import argparse
from src import NBAGameScraper


def main():
    """Main function to run the scraper"""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='NBA Game Data Scraper - Scrapes NBA game data from tw-nba.udn.com',
        usage='%(prog)s [URL] or %(prog)s --url [URL]'
    )

    # Accept URL as positional or optional argument
    parser.add_argument('url', nargs='?', help='URL of the NBA game to scrape')
    parser.add_argument('--url', '-u', dest='url_flag', help='URL of the NBA game to scrape')
    parser.add_argument('--output', '-o', help='Output filename (default: nba_game_data_[timestamp].xlsx)')

    args = parser.parse_args()

    # Get URL from either positional or flag argument
    url = args.url or args.url_flag

    # If no URL provided, use default or show help
    if not url:
        print("Error: No URL provided!")
        print("\nUsage examples:")
        print("  python main.py https://tw-nba.udn.com/nba/standings_game/[game-id]")
        print("  python main.py --url https://tw-nba.udn.com/nba/standings_game/[game-id]")
        print("\nDefault URL for testing:")
        print("  https://tw-nba.udn.com/nba/standings_game/534867d1-8ef1-4929-b32c-4f766f159017")

        # Ask if user wants to use default URL
        response = input("\nUse default URL for testing? (y/n): ")
        if response.lower() == 'y':
            url = "https://tw-nba.udn.com/nba/standings_game/534867d1-8ef1-4929-b32c-4f766f159017"
        else:
            sys.exit(1)

    print("Starting NBA Game Scraper...")
    print("=" * 50)
    print(f"URL: {url}")

    scraper = NBAGameScraper(url)
    success = scraper.scrape()

    if success:
        print("=" * 50)
        print("Scraping completed successfully!")
        print(f"Total player stats collected: {len(scraper.player_stats)}")
        print(f"Total team stats collected: {len(scraper.team_stats)}")
        if hasattr(scraper, 'all_data'):
            print(f"Total tables found: {len(scraper.all_data.get('tables', []))}")
    else:
        print("Scraping failed. Please check the error messages above.")


if __name__ == "__main__":
    main()