"""
NBA Game Data Scraper
Scrapes NBA game data from tw-nba.udn.com and saves to Excel
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import os


class NBAGameScraper:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.game_data = {}
        self.team_stats = []
        self.player_stats = []
        self.team_names = []  # Store team names [home, away] with format Chinese(English)
        self.team_names_chinese = []  # Store Chinese-only team names for filename

        # NBA Team name mapping (Chinese to English)
        self.team_name_mapping = {
            '塞爾蒂克': 'Celtics', '塞爾提克': 'Celtics', '凱爾特人': 'Celtics',
            '籃網': 'Nets', '布魯克林籃網': 'Nets',
            '尼克': 'Knicks', '紐約尼克': 'Knicks',
            '76人': '76ers', '七六人': '76ers',
            '暴龍': 'Raptors', '速龍': 'Raptors',
            '公牛': 'Bulls', '芝加哥公牛': 'Bulls',
            '騎士': 'Cavaliers', '克里夫蘭騎士': 'Cavaliers',
            '活塞': 'Pistons', '底特律活塞': 'Pistons',
            '溜馬': 'Pacers', '印第安納溜馬': 'Pacers',
            '公鹿': 'Bucks', '密爾瓦基公鹿': 'Bucks',
            '老鷹': 'Hawks', '亞特蘭大老鷹': 'Hawks',
            '黃蜂': 'Hornets', '夏洛特黃蜂': 'Hornets',
            '熱火': 'Heat', '邁阿密熱火': 'Heat',
            '魔術': 'Magic', '奧蘭多魔術': 'Magic',
            '巫師': 'Wizards', '華盛頓巫師': 'Wizards',
            '金塊': 'Nuggets', '丹佛金塊': 'Nuggets',
            '灰狼': 'Timberwolves', '明尼蘇達灰狼': 'Timberwolves',
            '雷霆': 'Thunder', '俄克拉荷馬雷霆': 'Thunder',
            '拓荒者': 'Trail Blazers', '波特蘭拓荒者': 'Trail Blazers',
            '爵士': 'Jazz', '猶他爵士': 'Jazz',
            '勇士': 'Warriors', '金州勇士': 'Warriors',
            '快艇': 'Clippers', '洛杉磯快艇': 'Clippers',
            '湖人': 'Lakers', '洛杉磯湖人': 'Lakers',
            '太陽': 'Suns', '鳳凰城太陽': 'Suns',
            '國王': 'Kings', '沙加緬度國王': 'Kings',
            '小牛': 'Mavericks', '獨行俠': 'Mavericks', '達拉斯獨行俠': 'Mavericks',
            '火箭': 'Rockets', '休士頓火箭': 'Rockets',
            '灰熊': 'Grizzlies', '曼菲斯灰熊': 'Grizzlies',
            '鵜鶘': 'Pelicans', '紐奧良鵜鶘': 'Pelicans',
            '馬刺': 'Spurs', '聖安東尼奧馬刺': 'Spurs'
        }

    def fetch_page(self):
        """Fetch the webpage content"""
        try:
            print(f"Fetching data from: {self.url}")
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def parse_game_info(self, soup):
        """Parse basic game information"""
        try:
            # Try to find game date
            date_element = soup.find('div', class_='date') or soup.find('span', class_='date')
            if date_element:
                self.game_data['date'] = date_element.text.strip()

            # Find team names and scores
            team_elements = soup.find_all('div', class_='team-name') or soup.find_all('span', class_='team')
            score_elements = soup.find_all('div', class_='score') or soup.find_all('span', class_='score')

            if len(team_elements) >= 2:
                self.game_data['home_team'] = team_elements[0].text.strip()
                self.game_data['away_team'] = team_elements[1].text.strip()

            if len(score_elements) >= 2:
                self.game_data['home_score'] = score_elements[0].text.strip()
                self.game_data['away_score'] = score_elements[1].text.strip()

            print(f"Game info parsed: {self.game_data}")

        except Exception as e:
            print(f"Error parsing game info: {e}")

    def parse_quarter_scores(self, soup):
        """Parse quarter by quarter scores"""
        try:
            quarter_data = []

            # Look for quarter scores in various possible formats
            quarter_table = soup.find('table', class_='quarter-scores') or \
                           soup.find('div', class_='quarter-breakdown')

            if quarter_table:
                rows = quarter_table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if cols:
                        quarter_data.append([col.text.strip() for col in cols])

            if quarter_data:
                df_quarters = pd.DataFrame(quarter_data)
                return df_quarters

        except Exception as e:
            print(f"Error parsing quarter scores: {e}")

        return pd.DataFrame()

    def parse_player_stats(self, soup):
        """Parse player statistics"""
        try:
            # Find all tables that might contain player stats
            tables = soup.find_all('table')

            for table in tables:
                # Check if this is a player stats table
                headers = table.find_all('th')
                if any('MIN' in h.text or '分鐘' in h.text or 'PTS' in h.text or '得分' in h.text for h in headers):
                    # Parse headers
                    header_row = [th.text.strip() for th in headers]

                    # Parse player data
                    rows = table.find_all('tr')[1:]  # Skip header row
                    for row in rows:
                        cols = row.find_all(['td', 'th'])
                        if cols:
                            player_data = {}
                            for i, col in enumerate(cols):
                                if i < len(header_row):
                                    player_data[header_row[i]] = col.text.strip()

                            if player_data:
                                self.player_stats.append(player_data)

            print(f"Found {len(self.player_stats)} player statistics")

        except Exception as e:
            print(f"Error parsing player stats: {e}")

    def parse_team_stats(self, soup):
        """Parse team statistics"""
        try:
            # Find team statistics
            team_stats_section = soup.find('div', class_='team-stats') or \
                                soup.find('table', class_='team-comparison')

            if team_stats_section:
                stat_items = team_stats_section.find_all(['div', 'tr'], class_=re.compile('stat'))

                for item in stat_items:
                    stat_name = item.find(class_=re.compile('stat-name|category'))
                    home_value = item.find(class_=re.compile('home|team1'))
                    away_value = item.find(class_=re.compile('away|team2'))

                    if stat_name:
                        self.team_stats.append({
                            'statistic': stat_name.text.strip(),
                            'home_team': home_value.text.strip() if home_value else '',
                            'away_team': away_value.text.strip() if away_value else ''
                        })

            print(f"Found {len(self.team_stats)} team statistics")

        except Exception as e:
            print(f"Error parsing team stats: {e}")

    def extract_team_names(self, table_data):
        """Extract team names from quarter scores table"""
        if table_data and len(table_data) >= 2:
            # Usually team names are in the second column of the quarter scores table
            for row in table_data:
                if len(row) >= 2:
                    team_name = row[1] if row[1] and row[1] not in ['Q1', 'Q2', 'Q3', 'Q4'] else None
                    if team_name and team_name in self.team_name_mapping:
                        chinese_name = team_name
                        english_name = self.team_name_mapping.get(team_name, team_name)
                        self.team_names.append(f"{chinese_name}({english_name})")
                        self.team_names_chinese.append(chinese_name)  # Store Chinese-only name

    def parse_all_data(self, soup):
        """Parse all available data from the page"""
        # Try to extract all possible data structures
        all_data = {
            'tables': [],
            'lists': [],
            'divs_with_data': []
        }

        # Extract all tables
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            table_data = []
            rows = table.find_all('tr')

            for row in rows:
                cols = row.find_all(['td', 'th'])
                row_data = [col.text.strip() for col in cols]
                if row_data:
                    table_data.append(row_data)

            if table_data:
                all_data['tables'].append({
                    'table_index': i,
                    'data': table_data
                })

                # Try to extract team names from the first table (quarter scores)
                if i == 0 and not self.team_names:
                    self.extract_team_names(table_data)

        # Extract structured divs with numerical data
        data_divs = soup.find_all('div', class_=re.compile('stat|score|point|player|team'))
        for div in data_divs:
            text = div.text.strip()
            if text and any(char.isdigit() for char in text):
                all_data['divs_with_data'].append(text)

        return all_data

    def save_to_excel(self, filename='nba_game_data.xlsx'):
        """Save all scraped data to Excel file"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Save game info
                if self.game_data:
                    df_game = pd.DataFrame([self.game_data])
                    df_game.to_excel(writer, sheet_name='Game Info', index=False)

                # Save player stats
                if self.player_stats:
                    df_players = pd.DataFrame(self.player_stats)
                    df_players.to_excel(writer, sheet_name='Player Stats', index=False)

                # Save team stats
                if self.team_stats:
                    df_teams = pd.DataFrame(self.team_stats)
                    df_teams.to_excel(writer, sheet_name='Team Stats', index=False)

                # Process raw scraped data
                if hasattr(self, 'all_data'):
                    team_sheet_count = 0
                    team_season_stats = []  # Collect team season statistics

                    # Mapping for statistics categories
                    stat_mapping = {
                        '得分': 'Points per Game',
                        '助攻': 'Assists per Game',
                        '籃板': 'Rebounds per Game',
                        '阻攻': 'Blocks per Game',
                        '抄截': 'Steals per Game',
                        '投籃%': 'Field Goal %',
                        '3分%': '3-Point %',
                        '罰球%': 'Free Throw %',
                        '失誤': 'Turnovers per Game'
                    }

                    for i, table_info in enumerate(self.all_data.get('tables', [])):
                        if table_info['data']:
                            df_table = pd.DataFrame(table_info['data'])

                            # Check if this is a player stats table (Tables 2 and 3)
                            if i > 0 and any('先發' in str(row) or '位置' in str(row) for row in table_info['data'][0] if row):
                                if team_sheet_count < len(self.team_names):
                                    sheet_name = f"{self.team_names[team_sheet_count]}_Players"[:31]
                                    team_sheet_count += 1
                                    df_table.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                                else:
                                    df_table.to_excel(writer, sheet_name=f'Table_{i+1}'[:31], index=False, header=False)

                            # Check if this is a team season stats table (Tables 4-12)
                            # These tables have 3 rows: stat name row, team1 row, team2 row
                            elif (len(table_info['data']) == 3 and
                                  len(table_info['data'][0]) == 1 and  # First row has stat name only
                                  len(table_info['data'][1]) == 3 and  # Second row has team data
                                  len(table_info['data'][2]) == 3):    # Third row has team data
                                # Extract statistic category from the first row
                                stat_category = table_info['data'][0][0]  # First row contains stat name

                                if stat_category in stat_mapping:
                                    # Process both teams' data (rows 1 and 2)
                                    for row_idx in [1, 2]:
                                        row = table_info['data'][row_idx]
                                        if len(row) >= 3:
                                            team_name = row[0]
                                            value = row[1]
                                            rank = row[2]

                                            # Get English name for the team
                                            english_name = self.team_name_mapping.get(team_name, team_name)

                                            team_season_stats.append({
                                                'Team': f"{team_name}({english_name})",
                                                'Statistic': stat_mapping[stat_category],
                                                'Value': value,
                                                'League Rank': rank
                                            })

                            # For quarter scores (Table 1)
                            elif i == 0:
                                df_table.to_excel(writer, sheet_name='Quarter Scores', index=False, header=False)

                            # Any other tables that don't match the patterns
                            else:
                                # Only save if not a team stats table
                                if not (len(table_info['data']) == 3 and
                                       len(table_info['data'][0]) == 1 and
                                       len(table_info['data'][1]) == 3 and
                                       len(table_info['data'][2]) == 3):
                                    df_table.to_excel(writer, sheet_name=f'Table_{i+1}'[:31], index=False, header=False)

                    # Save consolidated team season statistics
                    if team_season_stats:
                        # Create a pivot table for better readability
                        df_team_stats = pd.DataFrame(team_season_stats)

                        # Pivot to have teams as columns and statistics as rows
                        pivot_stats = df_team_stats.pivot_table(
                            index='Statistic',
                            columns='Team',
                            values='Value',
                            aggfunc='first'
                        )

                        # Also create a ranking pivot
                        pivot_ranks = df_team_stats.pivot_table(
                            index='Statistic',
                            columns='Team',
                            values='League Rank',
                            aggfunc='first'
                        )

                        # Combine values and ranks
                        combined_data = []
                        for stat in pivot_stats.index:
                            row_data = {'Statistic': stat}
                            for team in pivot_stats.columns:
                                if team in pivot_stats.columns:
                                    value = pivot_stats.loc[stat, team]
                                    rank = pivot_ranks.loc[stat, team] if team in pivot_ranks.columns else ''
                                    row_data[f'{team} Value'] = value
                                    row_data[f'{team} Rank'] = rank
                            combined_data.append(row_data)

                        df_combined = pd.DataFrame(combined_data)

                        # Save the consolidated team statistics
                        df_combined.to_excel(writer, sheet_name='Team Season Statistics', index=False)

                        print(f"Consolidated {len(team_season_stats)} team statistics entries")

                print(f"Data saved to {filename}")
                print(f"Team names found: {self.team_names}")
                return True

        except Exception as e:
            print(f"Error saving to Excel: {e}")
            return False

    def scrape(self):
        """Main scraping method"""
        html_content = self.fetch_page()

        if not html_content:
            print("Failed to fetch page content")
            return False

        soup = BeautifulSoup(html_content, 'lxml')

        # Parse different sections
        self.parse_game_info(soup)
        self.parse_quarter_scores(soup)
        self.parse_player_stats(soup)
        self.parse_team_stats(soup)

        # Parse all data as backup
        self.all_data = self.parse_all_data(soup)

        # Create output directory if it doesn't exist
        output_dir = "output_excel"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")

        # Generate filename with team names and date
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Use team names if available, otherwise use default naming
        if len(self.team_names_chinese) >= 2:
            team1 = self.team_names_chinese[0]
            team2 = self.team_names_chinese[1]
            filename = f"{team1}_{team2}_{date_str}.xlsx"
        else:
            # Fallback to default naming if team names not found
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nba_game_data_{timestamp}.xlsx"

        # Full path with output directory
        full_path = os.path.join(output_dir, filename)

        # Save to Excel
        success = self.save_to_excel(full_path)

        return success